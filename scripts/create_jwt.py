#!/usr/bin/env python3
import argparse, datetime as dt, jwt, os, json

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sub", required=True, help="subject/email")
    ap.add_argument("--role", default="analyst", help="role claim")
    ap.add_argument("--secret", default=os.environ.get("JWT_SECRET","dev-secret"))
    ap.add_argument("--exp", type=int, default=60, help="minutes")
    args = ap.parse_args()

    now = dt.datetime.utcnow()
    payload = {
        "sub": args.sub,
        "role": args.role,
        "iat": int(now.timestamp()),
        "exp": int((now + dt.timedelta(minutes=args.exp)).timestamp()),
    }
    token = jwt.encode(payload, args.secret, algorithm="HS256")
    print(token)

if __name__ == "__main__":
    main()
