(define (problem m-pb1)
  (:domain ma-blocksworld)
  (:objects a b ag1 ag2 ag3)
  (:init (onTable a) (onTable b) (clear a) (clear b) (equal a a) (equal b b) (agent ag1) (agent ag2) (agent ag3))
  (:goal (on a b))
 )