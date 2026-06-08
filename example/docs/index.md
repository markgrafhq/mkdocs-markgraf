# markgraf in mkdocs

Animated diagrams rendered by the Canvas2D embed bundle. Each fenced
`markgraf` block becomes a scrollable, scrubbable player.

## Cache insertion

A read path before and after introducing a cache.

```markgraf
seed 1

keyframe v1 {
  +node client "Client"
  +node api "API"
  +node db "Database"
  +edge client api
  +edge api db
  client -> api "GET /user/42"
  api -> db "SELECT"
}

keyframe v2 {
  +node cache "Cache"
  -edge api db
  +edge api cache
  client -> api "GET /user/42"
  api -> cache "HIT"
}
```

## Fan-out pipeline

Larger graph; constrained to a shorter height with `height=320`.

```markgraf height=320
seed 2

keyframe ingest {
  +node src "Producer"
  +node q "Queue"
  +node w1 "Worker 1"
  +node w2 "Worker 2"
  +node w3 "Worker 3"
  +node sink "Sink"
  +edge src q
  +edge q w1
  +edge q w2
  +edge q w3
  +edge w1 sink
  +edge w2 sink
  +edge w3 sink
  src -> q "batch"
}

keyframe work {
  q -> w1 "job 1"
  q -> w2 "job 2"
  q -> w3 "job 3"
}

keyframe drain {
  w1 -> sink "done 1"
  w2 -> sink "done 2"
  w3 -> sink "done 3"
}
```

## Narrow embed

Same diagram clamped to a narrow column with `width=420`.

```markgraf width=420
seed 3

keyframe v1 {
  +node a "Auth"
  +node b "Billing"
  +node c "Catalog"
  +edge a b
  +edge b c
  a -> b "token"
  b -> c "price?"
}

keyframe v2 {
  c -> b "$9.99"
  b -> a "ok"
}
```

## Tall layout

Using `height=80svh` lets a deep graph use most of the viewport.

```markgraf height=80svh
seed 4

keyframe v1 {
  +node ui "UI"
  +node gw "Gateway"
  +node svc "Service"
  +node cache "Cache"
  +node db "Primary DB"
  +node replica "Replica"
  +edge ui gw
  +edge gw svc
  +edge svc cache
  +edge svc db
  +edge db replica
  ui -> gw "request"
  gw -> svc "forward"
}

keyframe v2 {
  svc -> cache "miss"
  svc -> db "SELECT"
  db -> replica "stream"
  db -> svc "row"
  svc -> gw "200"
  gw -> ui "json"
}
```

## Cache write — the full story

Seven frames: naive read → DB joins → cache → naive write → stale read → fix
with cache invalidation → rerun that's now correct. Multi-line `|…|` token
labels narrate each hop.

```markgraf height=70svh
seed 1

keyframe "a simple read" {
  +node client "Client"
  +node api    "API"
  +edge client api

  client -> api |GET /user/42
asks the API
for one user record|
}

keyframe "DB joins the story" {
  +node db "Database"
  +edge api db

  client -> api |GET /user/42
arrives at the API|

  api -> db |the API falls through
to the source of truth|

  api <- db |the row comes back,
fresh from disk|

  client <- api |200 OK
correct, but every read
costs a DB round trip|
}

keyframe "add a cache to speed up reads" {
  +node cache "Cache"
  +edge api cache
}

keyframe "naive write: forget the cache" {
  client -> api |POST /user/42
updates the user's row|

  api -> db |INSERT
writes to the DB,
the source of truth|

  client <- api |201 Created
looks fine, but the cache
still holds the OLD row|
}

keyframe "the catch: a stale read" {
  client -> api |GET /user/42
asks for the row we
just overwrote|

  api -> cache |LOOKUP user:42
checks the cache,
since reads should be fast|

  api <- cache |HIT
the cache returns
the pre-write value|

  client <- api |200 OK
but the row is stale --
the user sees old data|
}

keyframe "fix: invalidate on write" {
  client -> api |POST /user/42
updates the user's row|

  api -> db |INSERT
writes to the DB|

  par {
    api -> cache |DEL user:42
drops the cache entry
so the next read refills|

    client <- api |201 Created
responds in parallel,
no waiting on the cache|
  }
}

keyframe "rerun: same GET, now correct" {
  client -> api |GET /user/42
asks for the row again|

  api -> cache |LOOKUP user:42
checks the cache first|

  api <- cache |MISS
the cache was just
invalidated|

  api -> db |SELECT
falls through to the DB|

  api <- db |the fresh row
comes back from disk|

  client <- api |200 OK
the user sees the
correct, current row|
}
```
