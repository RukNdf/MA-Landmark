from recognizer.pddl.pddl_planner import applicable
from recognizer.pddl.pddl_parser import PDDL_Parser
from recognizer.plan_recognizer import PlanRecognizer
#from heuristics import landmarks
import itertools 

class HeurPlanRecognizer(PlanRecognizer):

    name = "Heur"

    def __init__(self, options=None):
        PlanRecognizer.__init__(self, options)
        
    def hgc(self, parser, treshold, threads):
        #
        #Compute Achieved Landmarks From Observations
        #
        num_hyp = len(self.hyps)
        action_dic = dict()
        for action in parser.actions:
            action_dic[action.name] = action
            
        achieved_landmarks = list()
        total_landmarks = set()
        all_goal_landmarks = list()
        total_achieved_landmarks = set()
        initial_achieved_landmarks = set()
        goals = list()
        #al1 for each goal G in g do
        for i in range(num_hyp):
            hyp_problem = "./"+self.options.work_dir+'/'+'hyp_%d_problem.pddl' % i
            parser.parse_problem(hyp_problem)
            
            goals.append((parser.positive_goals, parser.negative_goals))
            achieved_landmarks.append(set())
            goal_landmarks = get_landmarks(parser, threads)
            all_goal_landmarks.append(goal_landmarks)
            total_landmarks.update(goal_landmarks)
            total_achieved_landmarks.update([l for l in goal_landmarks if l in parser.state])
            
            #al1 for each observed action o in O do
            for observation in self.observations:
                obs = observation[1:-1].split(' ')
                observed_action = action_dic[obs[0]].add_param(obs[1:])
                achieved_landmarks[i].update([l for l in goal_landmarks if l in observed_action.positive_preconditions])
                achieved_landmarks[i].update([l for l in goal_landmarks if l in observed_action.add_effects])
        
        initial_landmarks = total_achieved_landmarks
        for i in range(num_hyp):
            total_achieved_landmarks.update(achieved_landmarks[i])
            achieved_landmarks[i].update(initial_landmarks)
            all_goal_landmarks[i].update(initial_landmarks)
        
        #al2 maxh 
        hgc_val = list()
        maxh = 0
        for i in range(num_hyp):
            count = 0
            aux = 0
            #positive goals
            for goal in goals[i][0]:
                goal_landmarks = get_filtered_landmarks(parser, all_goal_landmarks[i], goal, True)
                aux += len([x for x in goal_landmarks if x in total_achieved_landmarks])/float(len(goal_landmarks))
                count += 1
            #negative goals
            for goal in goals[i][1]:
                goal_landmarks = get_filtered_landmarks(parser, all_goal_landmarks[i], goal, False)
                aux += len([x for x in goal_landmarks if x in total_achieved_landmarks])/float(len(goal_landmarks))
                count += 1
            aux /= count
            hgc_val.append(aux)
            if(aux> maxh):
                maxh = aux
                
        #al2 return all G -
        positive_goals = set()
        negative_goals = set()
        for i in range(num_hyp):
            if(hgc_val[i] >= (maxh-treshold)):
                positive_goals.update(goals[i][0])
                negative_goals.update(goals[i][1])
        return (positive_goals, negative_goals)
        
    def huniq(self, parser, treshold, threads):
        #
        #Compute Achieved Landmarks From Observations
        #
        num_hyp = len(self.hyps)
        action_dic = dict()
        for action in parser.actions:
            action_dic[action.name] = action
            
        achieved_landmarks = list()
        total_landmarks = set()
        all_goal_landmarks = list()
        total_achieved_landmarks = set()
        initial_achieved_landmarks = set()
        goals = list()
        #al1 for each goal G in g do
        for i in range(num_hyp):
            hyp_problem = "./"+self.options.work_dir+'/'+'hyp_%d_problem.pddl' % i
            parser.parse_problem(hyp_problem)
            
            goals.append((parser.positive_goals, parser.negative_goals))
            achieved_landmarks.append(set())
            goal_landmarks = get_landmarks(parser, threads)
            all_goal_landmarks.append(goal_landmarks)
            total_landmarks.update(goal_landmarks)
            total_achieved_landmarks.update([l for l in goal_landmarks if l in parser.state])
            
            #al1 for each observed action o in O do
            for observation in self.observations:
                obs = observation[1:-1].split(' ')
                observed_action = action_dic[obs[0]].add_param(obs[1:])
                achieved_landmarks[i].update([l for l in goal_landmarks if l in observed_action.positive_preconditions])
                achieved_landmarks[i].update([l for l in goal_landmarks if l in observed_action.add_effects])
        
        initial_landmarks = total_achieved_landmarks
        for i in range(num_hyp):
            total_achieved_landmarks.update(achieved_landmarks[i])
            achieved_landmarks[i].update(initial_landmarks)
            all_goal_landmarks[i].update(initial_landmarks)
            
        #al3 for each fac landmark l in lg do
        yuv = dict()
        for landmark in total_landmarks:
            yuv[landmark] = LUniq(landmark, all_goal_landmarks)
        
        #al3 maxh 
        hval = list()
        maxh = 0
        for i in range(num_hyp):
            divid = 0.0
            divis = 0.0
            for achieved_landmark in achieved_landmarks[i]:
                divid += yuv[achieved_landmark]
            for landmark in all_goal_landmarks[i]:
                divis += yuv[landmark]
            aux = divid/divis
            hval.append(aux)
            if(aux> maxh):
                maxh = aux
                
        #al3 return all G -
        positive_goals = set()
        negative_goals = set()
        for i in range(num_hyp):
            if(hval[i] >= (maxh-treshold)):
                positive_goals.update(goals[i][0])
                negative_goals.update(goals[i][1])
        return (positive_goals, negative_goals)
    
    
    def run_recognizer(self, type, treshold, threads):
        domain_file = "./"+self.options.work_dir+'/'+self.options.domain_name+'.pddl'
        parser = PDDL_Parser()
        parser.parse_domain(domain_file)
        if type == 'hgc':
            self.unique_goal = self.hgc(parser, treshold, threads)
            return
        self.unique_goal = self.huniq(parser, treshold, threads)

        
def LUniq(landmark, total_landmarks):
    count = 0
    for landmarks in total_landmarks:
        if landmark in landmarks:
            count+=1
    return 1.0/count
    
    
import copy
from multiprocessing import Pool
#pyperplan
def get_landmarks(parser, threads):
    """ Returns a set of landmarks.
    In this implementation a fact is a landmark if the goal facts cannot be
    reached without it.
    """
    landmarks = list(parser.positive_goals)
    possible_landmarks = get_facts(parser)
    positive_landmarks = list()
    
    #landmarks for positive goals
    goal_reached = parser.state >= parser.positive_goals
    with Pool(threads) as process:
        results = process.starmap(aval_positive_fact, itertools.product([parser],possible_landmarks,[goal_reached]))
        
    for landmark, fact in results:
        if(landmark):
            positive_landmarks.append(fact)
   
    #landmarks for negative goals
    goal_reached = True            
    for negative_goal in parser.negative_goals:
        if negative_goal in parser.state:
            goal_reached = False
    if goal_reached:
        return set(landmarks)
            
    with Pool(threads) as process:
        results = process.starmap(aval_negative_fact, itertools.product([parser],[x for x in possible_landmarks if x not in positive_landmarks],[goal_reached]))
        
    for landmark, fact in results:
        if(landmark):
            landmarks.append(fact)
    
    return set(landmarks).union(positive_landmarks)
    
    
def aval_negative_fact(parser, fact, goal_reached):
    current_state = parser.state

    while not goal_reached:
        previous_state = current_state

        for ung_action in parser.actions:
            for action in ung_action.groundify(parser.objects):
                if action.applicable(current_state) and fact not in list(action.add_effects):
                    current_state = current_state.union(action.del_effects)
                    for negative_goal in parser.negative_goals:
                        if negative_goal in current_state:
                            continue
                    break
                        
        goal_reached = True            
        for negative_goal in parser.negative_goals:
            if negative_goal in current_state:
                goal_reached = False
        if previous_state == current_state and not goal_reached:
            return (True, fact)
    return (False, 0)
                
def aval_positive_fact(parser, fact, goal_reached):
    current_state = parser.state

    while not goal_reached:
        previous_state = current_state

        for ung_action in parser.actions:
            for action in ung_action.groundify(parser.objects):
                if action.applicable(current_state) and fact not in list(action.add_effects):
                    current_state = current_state.union(action.add_effects)
                    if current_state >= parser.positive_goals:
                        break
                        
        goal_reached = current_state >= parser.positive_goals
        if previous_state == current_state and not goal_reached:
            return (True, fact)
    return (False, 0)
    
#pyperplan
def get_filtered_landmarks(parser, possible_landmarks, goal, positive):
    """ Returns a set of landmarks.
    In this implementation a fact is a landmark if the goal facts cannot be
    reached without it.
    """
    landmarks = list()
    initial_state_goal_reached = test_goal_reached(parser.state, parser.positive_goals, parser.negative_goals)
    #landmarks for positive goals
    if positive:
        landmarks.append(goal)
        initial_state_goal_reached = goal in parser.state
        for fact in possible_landmarks:
            current_state = parser.state
            goal_reached = initial_state_goal_reached

            while not goal_reached:
                previous_state = current_state

                for ung_action in parser.actions:
                    for action in ung_action.groundify(parser.objects):
                        if action.applicable(current_state) and fact not in list(action.add_effects):
                            current_state = current_state.union(action.add_effects)
                            if goal in current_state:
                                break
                                
                goal_reached = goal in current_state
                if previous_state == current_state and not goal_reached:
                    landmarks.append(fact)
                    break
        return set(landmarks)
        
    #landmarks for negative goals
    initial_state_goal_reached = goal not in parser.state
    for fact in [x for x in possible_landmarks if x not in landmarks]:
        current_state = parser.state
        goal_reached = initial_state_goal_reached

        while not goal_reached:
            previous_state = current_state

            for ung_action in parser.actions:
                for action in ung_action.groundify(parser.objects):
                    if action.applicable(current_state) and fact not in list(action.add_effects):
                        current_state = current_state.union(action.del_effects)
                        if not goal in current_state:
                            break
                            
            goal_reached = True            
            if goal in current_state:
                goal_reached = False
            if previous_state == current_state and not goal_reached:
                landmarks.append(fact)
                break
    
    return set(landmarks)


def test_goal_reached(state, positive_goals, negative_goals):
    if not state >= positive_goals:
        #positive goals not reached
        return False
    for g in negative_goals:
        if g in state:
            #negative goals reached
            return False
    return True
    

#grounds predicates
def get_facts(parser):
    facts = list()
    for pnam, p in parser.predicates.items():
        fact = set()
        fact.add(pnam)
        aux = list()
        for t in p.items():
            if not t[1] in parser.objects:
                continue
            aux.append(parser.objects[t[1]])
        
        if len(aux) == 0:
            continue
            
        fact = set((x,y) for x in fact for y in aux[0])
        for i in range(1,len(aux)):
            fact = list(x+tuple(y) for x in fact for y in aux[i])
        
        facts += fact
    return facts

def test(goals, result):
    for goal in goals:
        aux = tuple(goal[1:-1].lower().split(' '))
        if aux[0] == 'not':
            aux = tuple(aux[1][1:-1].lower().split(' '))
            if not aux in result[1]:
                return False
        else:
            if not aux in result[0]:
                return False
    return True
        

import sys
import time
from recognizer.options import Options
from recognizer.problem import Hypothesis
def main():
    options = Options(sys.argv[1])
    options.domain_name = 'domain'
    options.verbose = False
    recognizer = HeurPlanRecognizer(options)
    #recognizer = SATPlanRecognizer(options)
    real_hypothesis = Hypothesis.load_real_hypothesis(sys.argv[1]+'real_hyp.dat')
    treshold = 0.1
    time_calc = time.monotonic() 
    recognizer.run_recognizer(sys.argv[2], float(sys.argv[3]), int(sys.argv[4]))
    time_calc = (time.monotonic() - time_calc)
    print(time_calc)
    print(test(real_hypothesis.atoms, recognizer.unique_goal))

if __name__ == '__main__':
    main()