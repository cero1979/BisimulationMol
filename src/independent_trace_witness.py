"""Full-rule tuple/product search validating a supplied finite visible word.

No compact state, truth table, projected graph, closure or simulation helper is
used. The original imported rule callbacks and all 28 model variables remain.
"""
from collections import deque


def accepts_model_trace(model,observables,word,withdraw=None,max_states=100000):
    start=(model.initial,0)
    seen,todo={start},deque([start])
    while todo:
        state,position=todo.popleft()
        if position==len(word):
            return {'accepted':True,'visited_product_states':len(seen),'status':'witness found'}
        values=dict(zip(model.variables,state))
        moves=[]
        for i,var in enumerate(model.variables):
            if var in model.constants:
                continue
            target=int(model.rules[var](values))
            if target!=state[i]:
                direction=1 if target>state[i] else -1
                action=var+('_up' if direction>0 else '_down') if var in observables else None
                if action is None or action==word[position]:
                    successor=state[:i]+(state[i]+direction,)+state[i+1:]
                    moves.append((successor,position+int(action is not None)))
        if withdraw is not None and values[withdraw]==1 and word[position]=='withdraw_'+withdraw:
            i=model.variables.index(withdraw)
            moves.append((state[:i]+(0,)+state[i+1:],position+1))
        for successor in moves:
            if successor not in seen:
                if len(seen)>=max_states:
                    return {'accepted':None,'visited_product_states':len(seen),'status':'inconclusive: cap'}
                seen.add(successor)
                todo.append(successor)
    return {'accepted':False,'visited_product_states':len(seen),'status':'exhausted exact product'}
