---
name: 05-docker-debug
description: Diagnoses container runtime failures using platform-specific failure modes and baseline diffs. Use when builds fail, containers exit immediately, or services cannot reach each other under Docker.
---

# Docker debugging (delta notes)

Framing: assume generic knowledge of `docker ps`, logs, and compose. This file lists facts that commonly trip people up on real machines.

## Baseline capture (do this first)

Record host OS and chip (`uname -a`, Apple Silicon vs x86_64), Docker edition (Docker Desktop vs Linux engine), compose file version, and whether SELinux or AppArmor is enforcing. Compare broken vs last known good: image digest, env vars, published ports, volume mounts, and DNS settings inside the container (`/etc/resolv.conf`).

## Platform deltas

- **macOS and Windows Desktop** — Container processes run inside a Linux VM; `host.docker.internal` exists for reaching the host, but **not** on native Linux unless explicitly added. Bind mounts use virtiofs/osxfs: case sensitivity and `inotify` behavior differ from Linux servers; file watcher storms can stall containers.
- **Apple Silicon** — Images built for `linux/amd64` run through emulation unless `platform: linux/arm64` (or multi-arch images) are used. Symptom: slow boot or `exec format error` when binaries lack arm64 builds.
- **Linux host** — `network_mode: host` behaves as expected; on Desktop it often does **not** map the same way because of the VM boundary.

## Networking gotchas

- **Published ports on wrong interface** — `0.0.0.0` vs `127.0.0.1` changes who can reach the service; remote teammates see “connection refused” when the bind address is loopback-only.
- **IPv6-only environments** — Some stacks resolve names to AAAA first; if the app binds IPv4 only, failures look like intermittent timeouts.
- **Embedded DNS** — Internal compose DNS fails if corporate VPN captures all traffic; symptom: resolves on host, fails in container. Fix paths include VPN split tunneling or overriding `dns` in compose (temporary).
- **Firewall chains (nftables/iptables)** — `DOCKER-USER` chain can drop forwarded traffic to custom bridge networks after reboots or VPN connect events.

## Storage and permissions

- **UID/GID mismatch** — Named volumes often map as root inside the container while bind mounts keep host ownership; symptom: permission denied writing to `./data`. Fix with matching user in Dockerfile, `user:` in compose, or `chown` on the host path (know the security tradeoff).
- **Read-only root** — Kubernetes and hardened compose files set `read_only: true`; crashes right after start if the app expects writable `/tmp` or `/var/run`.
- **Line endings on bind-mounted scripts** — CRLF from Windows hosts breaks `#!/bin/sh` entrypoints with `^M: not found`.

## Build vs runtime

- **BuildKit cache** — Stale layers can hide “works on rebuild” bugs; `docker build --no-cache` isolates Dockerfile issues.
- **ARG vs ENV** — Build-time `ARG` values do not persist into runtime unless copied to `ENV`; symptom: variable present during build, missing in running container.
- **Multi-stage discard** — Files created only in an earlier stage are absent in the final image if not copied with `COPY --from`.

## Orchestrator-specific (Compose)

- **Service name DNS** — On custom networks, use the service name as hostname, not `localhost`, unless sharing a network namespace.
- **Depends_on without health** — Containers start in order but do not wait for readiness; databases accept TCP while still initializing, causing migrate failures.
- **Profile gaps** — `docker compose up` without the right `--profile` skips services silently; debugging looks like “port not listening”.

## Minimal triage order

1. `docker inspect` exit code and `State.Error` for immediate crashes.
2. Last 200 log lines with timestamps; enable debug flags for the app if available.
3. Exec in: `docker exec -it <id> sh` then `ping`, `nc`, or `curl` to the expected upstream using the same address the app uses.
4. Diff env, mounts, and image digest against the last working deploy.

## When to stop guessing

Escalate to image maintainers or infra if seccomp/AppArmor profiles, FUSE mounts, or GPU device nodes are in play — reproduction without the same host flags wastes time.
