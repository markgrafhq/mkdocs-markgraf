# markgraf in mkdocs

Animated diagrams rendered by the Canvas2D embed bundle. Each fenced
`markgraf` block becomes a scrollable, scrubbable player.

## Cache insertion

A read path before and after introducing a cache.

```markgraf
seed 1

scene v1 {
  + client: Client
  + api: API
  + db: Database
  + client -> api
  + api -> db
  client ~> api: GET /user/42
  api ~> db: SELECT
}

scene v2 {
  + cache: Cache
  - api -> db
  + api -> cache
  client ~> api: GET /user/42
  api ~> cache: HIT
}
```

## Fan-out pipeline

Larger graph; constrained to a shorter height with `height=320`.

```markgraf height=320
seed 2

scene ingest {
  + src: Producer
  + q: Queue
  + w1: Worker 1
  + w2: Worker 2
  + w3: Worker 3
  + sink: Sink
  + src -> q
  + q -> w1
  + q -> w2
  + q -> w3
  + w1 -> sink
  + w2 -> sink
  + w3 -> sink
  src ~> q: batch
}

scene work {
  q ~> w1: job 1
  q ~> w2: job 2
  q ~> w3: job 3
}

scene drain {
  w1 ~> sink: done 1
  w2 ~> sink: done 2
  w3 ~> sink: done 3
}
```

## Narrow embed

Same diagram clamped to a narrow column with `width=420`.

```markgraf width=420
seed 3

scene v1 {
  + a: Auth
  + b: Billing
  + c: Catalog
  + a -> b
  + b -> c
  a ~> b: token
  b ~> c: price?
}

scene v2 {
  c ~> b: $9.99
  b ~> a: ok
}
```

## Tall layout

Using `height=80svh` lets a deep graph use most of the viewport.

```markgraf height=80svh
seed 4

scene v1 {
  + ui: UI
  + gw: Gateway
  + svc: Service
  + cache: Cache
  + db: Primary DB
  + replica: Replica
  + ui -> gw
  + gw -> svc
  + svc -> cache
  + svc -> db
  + db -> replica
  ui ~> gw: request
  gw ~> svc: forward
}

scene v2 {
  svc ~> cache: miss
  svc ~> db: SELECT
  db ~> replica: stream
  db ~> svc: row
  svc ~> gw: 200
  gw ~> ui: json
}
```

## Cache write — the full story

Seven frames: naive read → DB joins → cache → naive write → stale read → fix
with cache invalidation → rerun that's now correct. Multi-line `|…|` token
labels narrate each hop.

```markgraf height=70svh
seed 1

scene "a simple read" {
  + client: Client
  + api: API
  + client -> api

  client ~> api |GET /user/42
asks the API
for one user record|
}

scene "DB joins the story" {
  + db: Database
  + api -> db

  client ~> api |GET /user/42
arrives at the API|

  api ~> db |the API falls through
to the source of truth|

  api <~ db |the row comes back,
fresh from disk|

  client <~ api |200 OK
correct, but every read
costs a DB round trip|
}

scene "add a cache to speed up reads" {
  + cache: Cache
  + api -> cache
}

scene "naive write: forget the cache" {
  client ~> api |POST /user/42
updates the user's row|

  api ~> db |INSERT
writes to the DB,
the source of truth|

  client <~ api |201 Created
looks fine, but the cache
still holds the OLD row|
}

scene "the catch: a stale read" {
  client ~> api |GET /user/42
asks for the row we
just overwrote|

  api ~> cache |LOOKUP user:42
checks the cache,
since reads should be fast|

  api <~ cache |HIT
the cache returns
the pre-write value|

  client <~ api |200 OK
but the row is stale --
the user sees old data|
}

scene "fix: invalidate on write" {
  client ~> api |POST /user/42
updates the user's row|

  api ~> db |INSERT
writes to the DB|

  par {
    api ~> cache |DEL user:42
drops the cache entry
so the next read refills|

    client <~ api |201 Created
responds in parallel,
no waiting on the cache|
  }
}

scene "rerun: same GET, now correct" {
  client ~> api |GET /user/42
asks for the row again|

  api ~> cache |LOOKUP user:42
checks the cache first|

  api <~ cache |MISS
the cache was just
invalidated|

  api ~> db |SELECT
falls through to the DB|

  api <~ db |the fresh row
comes back from disk|

  client <~ api |200 OK
the user sees the
correct, current row|
}
```
