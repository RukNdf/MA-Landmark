(define (problem m-pb5b)
  (:domain ma-blocksworld)
  (:objects a b c d e f ag1 ag2 ag3)
  (:init (onTable a) (onTable b) (onTable c) (onTable d) (onTable e) (onTable f)
    (clear a) (clear b) (clear c) (clear d) (clear e) (clear f)
    (equal a a) (equal b b) (equal c c) (equal d d) (equal e e) (equal f f)
    (agent ag1) (agent ag2) (agent ag3)
    )
  (:goal (and (on a b) (on c d) (on e f))))