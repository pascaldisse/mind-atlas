#!/usr/bin/env python3
"""raw/ の committable 冗長化。データ変更ゼロ (読むだけ)。

出力 (runs/<runid>/):
  raw-sha256.tsv        相対path <TAB> sha256  (sorted, LF)
  raw-archive.tar.gz    決定的tar (sorted / mtime=0 / uid=gid=0 / gzip mtime=0)

用法:
  python3 scripts/archive_raw.py <runid> [...]      生成
  python3 scripts/archive_raw.py --verify <runid>   raw/ と成果物の一致検証

PREREG §6 は raw/ を gitignore と宣言 → 本artifactは §6 からの逸脱であり、
operator 裁定 (2026-08-07) による。逸脱の記録は results/FINAL-lighthouse-r5.md §逸脱。
"""
import gzip, hashlib, io, os, sys, tarfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def rels(rawdir):
    out = []
    for d, _, fs in os.walk(rawdir):
        for f in fs:
            out.append(os.path.relpath(os.path.join(d, f), rawdir))
    return sorted(out)


def manifest(rawdir):
    return "".join(f"{r}\t{sha256(os.path.join(rawdir,r))}\n" for r in rels(rawdir))


def build(runid):
    rd = os.path.join(ROOT, "runs", runid, "raw")
    assert os.path.isdir(rd), rd
    man = manifest(rd)
    n = man.count("\n")
    mp = os.path.join(ROOT, "runs", runid, "raw-sha256.tsv")
    with open(mp, "w", newline="\n") as f:
        f.write(man)

    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w", format=tarfile.PAX_FORMAT) as t:
        for r in rels(rd):
            p = os.path.join(rd, r)
            ti = tarfile.TarInfo(f"{runid}/raw/{r}")
            ti.size = os.path.getsize(p)
            ti.mtime = 0
            ti.mode = 0o644
            ti.uid = ti.gid = 0
            ti.uname = ti.gname = ""
            with open(p, "rb") as fh:
                t.addfile(ti, fh)
    ap = os.path.join(ROOT, "runs", runid, "raw-archive.tar.gz")
    with open(ap, "wb") as f:
        f.write(gzip.compress(buf.getvalue(), 9, mtime=0))
    print(f"{runid}: files={n} manifest={sha256(mp)[:16]}… "
          f"archive={sha256(ap)[:16]}… bytes={os.path.getsize(ap)}")


def verify(runid):
    rd = os.path.join(ROOT, "runs", runid, "raw")
    mp = os.path.join(ROOT, "runs", runid, "raw-sha256.tsv")
    live = manifest(rd)
    stored = open(mp).read()
    ok_man = live == stored
    ap = os.path.join(ROOT, "runs", runid, "raw-archive.tar.gz")
    got = {}
    with tarfile.open(ap, "r:gz") as t:
        for m in t.getmembers():
            got[m.name.split("/raw/", 1)[1]] = hashlib.sha256(
                t.extractfile(m).read()).hexdigest()
    want = dict(l.split("\t") for l in live.strip().split("\n"))
    ok_arc = got == want
    print(f"{runid}: n={len(want)} manifest={'OK' if ok_man else 'MISMATCH'} "
          f"archive={'OK' if ok_arc else 'MISMATCH'}")
    return ok_man and ok_arc


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--verify":
        sys.exit(0 if all([verify(r) for r in a[1:]]) else 1)
    for r in a:
        build(r)
