(define (problem pbTemplate)
   (:domain dwr)
   (:objects ca k2 r1 l1 cb cd cf l2 p2 cc ce q1 q2 p1 pallet k1  )
   (:init (on cc cb) (in ca p1) (on cb ca) (on cd pallet) (unloaded r1) (empty k1) (in cb p1) (on ca pallet) (at r1 l1) (on ce cd) (top cc p1) (top cf q1) (top pallet p2) (in ce q1) (empty k2) (top pallet q2) (occupied l1) (in cf q1) (in cc p1) (in cd q1) (on cf ce) )
   (:goal (and (in ce q2) (in cf q2) (in cc p2) (in cd q2) (in ca p2) (in cb q2) ) )
)