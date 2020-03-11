; (set-option :produce-unsat-cores true)
; (set-option :produce-proofs true)
(declare-const p_0 Bool)
(declare-const q_0 Bool)
(declare-const r_0 Bool)

(declare-const p_1 Bool)
(declare-const q_1 Bool)
(declare-const r_1 Bool)

(declare-const p_2 Bool)
(declare-const q_2 Bool)
(declare-const r_2 Bool)

(declare-sort Obs)

(declare-const p Obs)
(declare-const q Obs)
(declare-const r Obs)

(declare-fun orderObs (Obs) Int)
(declare-fun orderExec (Obs) Int)

(assert (= (orderObs p) 0))
(assert (= (orderObs q) 1))
(assert (= (orderObs r) 2))

(define-fun order-restriction1 () Bool
	(implies (and p_0) (= (orderExec p) 0) ) )
(define-fun order-restriction2 () Bool 
	(implies (and p_1) (= (orderExec p) 1) ) )
(define-fun order-restriction3 () Bool 
	(implies (and p_2) (= (orderExec p) 2) ) )


;(define-fun order-sync () Bool
;	(implies (< (orderObs p) (orderObs q)) (< (orderExec p) (orderExec q))))

(define-fun order-sync () Bool
    (forall ((x Obs) (y Obs)) (implies (< (orderObs x) (orderObs y)) (< (orderExec x) (orderExec y))) )
)

; (declare-fun order (Obs Bool) Int)
; (assert (= (order p p_0) 0))
; ; (assert (= (order q q_0) 0))
; ; (assert (= (order r r_0) 0))
; ; ;
; (assert (= (order p p_1) 1))
; ; (assert (= (order q q_1) 1))
; ; (assert (= (order r r_1) 1))
; ; ;
; (assert (= (order p p_2) 2))
; ; (assert (= (order q q_2) 2))
; ; (assert (= (order r r_2) 2))


; (assert (>= (order p p_2) (order q q_0)))

(assert (<= (orderObs p) (orderObs q)))

; (define-fun order-restriction () Bool
;     (exists ((x Bool))
;     (implies (and x)
;         (and (exists ((y Bool)) (<= (order y) (order x)) ) )
;     ))
; )

; (ite (check-sat) (get-model) (get-unsat-core))
(check-sat)
; (get-model)
; (get-unsat-core)
; (get-proofs)
; (get-value responses)
; (get-value (order p p_2))
; (get-value (order q q_0))
; (eval (order p p_2))