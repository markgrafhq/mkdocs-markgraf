# markgraf in mkdocs

Animated diagrams rendered by the Canvas2D embed bundle. Each fenced
`markgraf` block becomes a scrollable, scrubbable player.

## Cache insertion

A read path before and after introducing a cache.

```markgraf
seed 1

frame v1 {
  +node client "Client"
  +node api "API"
  +node db "Database"
  +edge client api
  +edge api db
  client -> api "GET /user/42"
  api -> db "SELECT"
}

frame v2 {
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

frame ingest {
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

frame work {
  q -> w1 "job 1"
  q -> w2 "job 2"
  q -> w3 "job 3"
}

frame drain {
  w1 -> sink "done 1"
  w2 -> sink "done 2"
  w3 -> sink "done 3"
}
```

## Narrow embed

Same diagram clamped to a narrow column with `width=420`.

```markgraf width=420
seed 3

frame v1 {
  +node a "Auth"
  +node b "Billing"
  +node c "Catalog"
  +edge a b
  +edge b c
  a -> b "token"
  b -> c "price?"
}

frame v2 {
  c -> b "$9.99"
  b -> a "ok"
}
```

## Tall layout

Using `height=80svh` lets a deep graph use most of the viewport.

```markgraf height=80svh
seed 4

frame v1 {
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

frame v2 {
  svc -> cache "miss"
  svc -> db "SELECT"
  db -> replica "stream"
  db -> svc "row"
  svc -> gw "200"
  gw -> ui "json"
}
```
