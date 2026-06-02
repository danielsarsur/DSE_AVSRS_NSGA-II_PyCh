from PyCh import *
import numpy as np
import random
from itertools import product
from collections import deque
from collections import defaultdict
from dataclasses import dataclass
import math
import time
from config import *
from control_policies import *

times = []

# Auxiliary functions
def get_movement_time(distance, vmax, acc, load_time):
    if distance <= (vmax**2 / acc):
        t_total = 2 * math.sqrt(distance / acc) + load_time
    else:
        t_total = distance / vmax + vmax / acc + load_time
    return t_total

def get_conveyor_time(aisle):
    return (((aisle + 1) * dc) / vc) + (lc * 2)

@dataclass
class Tote:
    entrytime: float = 0.0
    id: int = 0
    column: int = 0
    side: int = 0 # 0: Left, 1: Right
    tier: int = 0
    aisle: int = 0
    is_storage: bool = False

@process
def Storage_Generator(env, c_out, iat_store, empty_list):
    id = 0
    queue = []
    iat_dist = lambda: np.random.exponential(iat_store)
    e_iat = env.timeout(iat_dist())
    e_send = None
    
    while True:
        e_send = c_out.send(queue[0]) if queue else None
        events = [e_iat, e_send]
        selection = yield env.select(*events)
        
        if selected(e_send):
            queue.pop(0)
            e_send = None
        else:
            if len(empty_list) > len(queue) + 1:
                x = Tote(entrytime=env.now, is_storage=True, id=id)
                id += 2
                queue.append(x)
            e_iat = env.timeout(iat_dist())

@process
def Retrieval_Generator(env, c_out, iat_retrieve, occupied_list):
    id = 1
    queue = []
    iat_dist = lambda: np.random.exponential(iat_retrieve)
    e_iat = env.timeout(iat_dist())
    e_send = None
    
    while True:
        e_send = c_out.send(queue[0]) if queue else None
        events = [e_iat, e_send]
        selection = yield env.select(*events)

        if selected(e_send):
            queue.pop(0)
            e_send = None
        else:
            if len(occupied_list) > len(queue) + 1:
                x = Tote(entrytime=env.now, is_storage=False, id=id)
                id += 2
                queue.append(x)
            e_iat = env.timeout(iat_dist())

@process
def Storage_Controller(env, c_store_to_conv, c_per_aisle, empty_list, store_policy, c_inbound_changed, Aisles, Levels, buf_cap):
    waitlist = defaultdict(deque)
    tote = [None for _ in range(Aisles)]
    e_receive = None
    e_send = [None for _ in range(Aisles)]
    e_buffer_changed = [None for _ in range(Aisles)]
    bound_slots = np.full((Aisles, Levels), buf_cap)

    while True:
        e_receive = c_store_to_conv.receive()
        e_send = [c_per_aisle[i].send(tote[i]) if tote[i] is not None else None for i in range(Aisles)]
        e_buffer_changed = [c_inbound_changed[i].receive() for i in range(Aisles)]

        selection = yield env.select(e_receive, *e_send, *e_buffer_changed)

        if selected(e_receive):
            x = selection
            idx = store_policies[store_policy](empty_list)
            coord = empty_list.pop(idx)
            x.aisle, x.tier, x.column, x.side = coord
            waitlist[(x.aisle, x.tier)].append(x)
            e_receive = None
        
        elif any(selected(e) for e in e_buffer_changed):
            i = next(i for i, e in enumerate(e_buffer_changed) if selected(e))
            aisle_idx, tier_idx = selection
            bound_slots[aisle_idx, tier_idx] += 1
            e_buffer_changed[i] = None
        
        elif any(selected(e) for e in e_send):
            i = next(i for i, e in enumerate(e_send) if selected(e))
            tote[i] = None
            e_send[i] = None

        if waitlist:
            for i in range(Aisles):
                if tote[i] is None:
                    for j in range(Levels):
                        if bound_slots[i, j] > 0 and waitlist[(i, j)]:
                            x = waitlist[(i, j)].popleft()
                            bound_slots[i, j] -= 1
                            tote[i] = x
                            break

@process
def Retrieval_Controller(env, c_retrieve_order, c_retrieve_to_dem, occupied_list, retrieve_policy, c_outbound_changed, Aisles, Levels, buf_cap):
    waitlist = defaultdict(deque)
    tote = [[None for _ in range(Levels)] for _ in range(Aisles)]
    e_receive = None
    e_send = [[None for _ in range(Levels)] for _ in range(Aisles)]
    e_buffer_changed = [None for _ in range(Aisles)]
    bound_slots = np.full((Aisles, Levels), buf_cap)

    while True:
        e_receive = c_retrieve_order.receive()
        e_send = [[c_retrieve_to_dem[i][j].send(tote[i][j]) if tote[i][j] is not None else None for j in range(Levels)] for i in range(Aisles)]
        e_buffer_changed = [c_outbound_changed[i].receive() for i in range(Aisles)]

        selection = yield env.select(e_receive, *[e for row in e_send for e in row if e is not None], *e_buffer_changed)

        if selected(e_receive):
            x = selection
            idx = retrieval_policies[retrieve_policy](occupied_list)
            coord = occupied_list.pop(idx)
            x.aisle, x.tier, x.column, x.side = coord
            waitlist[(x.aisle, x.tier)].append(x)
            e_receive = None
        
        elif any(selected(e) for e in e_buffer_changed):
            i = next(i for i, e in enumerate(e_buffer_changed) if selected(e))
            aisle_idx, tier_idx = selection
            bound_slots[aisle_idx, tier_idx] += 1
            e_buffer_changed[i] = None
        
        elif any(e_send[i][j] is not None and selected(e_send[i][j]) for i in range(Aisles) for j in range(Levels)):
            i, j = next((i, j) for i in range(Aisles) for j in range(Levels) if e_send[i][j] is not None and selected(e_send[i][j]))
            tote[i][j] = None
            e_send[i][j] = None

        if waitlist:
            for i in range(Aisles):
                for j in range(Levels):
                    if tote[i][j] is None and bound_slots[i, j] > 0 and waitlist[(i, j)]:
                        x = waitlist[(i, j)].popleft()
                        bound_slots[i, j] -= 1
                        tote[i][j] = x

@process
def Conveyor(env, c_in, c_out):
    while True:
        tote = yield env.execute(c_in.receive())
        yield env.timeout(get_conveyor_time(tote.aisle))
        yield env.execute(c_out.send(tote))

@process
def Demand_Buffer(env, c_retrieve_to_dem, c_buf_to_dem, c_dem_to_veh, vehicle_policy):
    xs = []
    current_column = 0
    
    while True:
        e_ret = c_retrieve_to_dem.receive()
        e_store_notif = c_buf_to_dem.receive()
        e_send_to_veh = c_dem_to_veh.send(xs[vehicle_policies[vehicle_policy](xs, current_column)]) if len(xs) > 0 else None
        selection = yield env.select(e_ret, e_store_notif, e_send_to_veh)
        
        if selected(e_ret) or selected(e_store_notif):
            xs.append(selection)
        if e_send_to_veh and selected(e_send_to_veh):
            idx = vehicle_policies[vehicle_policy](xs, current_column)
            current_column = xs[idx].column
            xs.pop(idx)

@process
def Vehicle(env, c_dem_to_veh, c_veh_to_buf, c_buf_to_veh, c_selected_tote, c_store_done, buf_cap, occupied_list, empty_list):
    current_column = 0

    while True:
        x = yield env.execute(c_dem_to_veh.receive())
        coord = (x.aisle, x.tier, x.column, x.side)
        
        if x.is_storage:
            dist = dv * (current_column + buf_cap) # from current column to buffer
            yield env.timeout(get_movement_time(dist, vmaxv, av, lv))
            yield env.execute(c_selected_tote.send(x)) # request tote x from the buffer
            yield env.execute(c_buf_to_veh.receive()) # get tote from buffer
            dist = dv * (x.column + buf_cap) # from buffer to column
            yield env.timeout(get_movement_time(dist, vmaxv, av, lv))
            current_column = x.column
            occupied_list.append(coord) # place tote in the slot
            yield env.execute(c_store_done.send(env.now - x.entrytime)) # notify storage to monitor
        else:
            dist = dv * abs(x.column  - current_column) # from current column to next_column
            yield env.timeout(get_movement_time(dist, vmaxv, av, lv))
            empty_list.append(coord) # get tote from slot
            dist = dv * (x.column + buf_cap) # from retrieved column to buffer
            yield env.timeout(get_movement_time(dist, vmaxv, av, lv))
            current_column = 0
            yield env.execute(c_veh_to_buf.send(x)) #place tote in buffer

@process
def Lift(env, c_lift_ready, c_next_tier, c_buf_to_lift, c_lift_to_conv, c_conv_to_lift, c_lift_to_buf, c_lift_position):
    current_tier = 0
    
    while True:
        e_store = c_conv_to_lift.receive() # Wait for tote to store
        e_ready = c_lift_ready.send("ready") # Send availability confirmation to Buffer
        selection = yield env.select(e_store, e_ready)

        if selected(e_store):
            tote = selection
            dist = dl * current_tier # from current tier to lowest level to get tote
            yield env.timeout(get_movement_time(dist, vmaxl, al, ll))
            dist = dl * tote.tier # from lowest level to delivery tier
            yield env.timeout(get_movement_time(dist, vmaxl, al, ll))
            current_tier = tote.tier # tier where the item was deliered
            yield env.execute(c_lift_to_buf[tote.tier].send(tote))
            yield env.execute(c_lift_position.send(current_tier))
        else:
            next_tier = yield env.execute(c_next_tier.receive())
            dist = dl * abs(next_tier - current_tier) # from current tier to next tier
            yield env.timeout(get_movement_time(dist, vmaxl, al, ll))
            tote = yield env.execute(c_buf_to_lift.receive())
            dist = dl * next_tier # from next_tier to lowest level to deliver tote
            yield env.timeout(get_movement_time(dist, vmaxl, al, ll))
            current_tier = 0 #delivered at the lowest level
            yield env.execute(c_lift_to_conv.send(tote))
            yield env.execute(c_lift_position.send(current_tier))

@process
def Buffer(env, c_veh_to_buf, c_lift_ready, c_next_tier, c_buf_to_lift, c_lift_to_buf, c_buf_to_dem, c_buf_to_veh, c_selected_tote, buf_cap, Levels, c_inbound_changed, c_outbound_changed, c_lift_position, lift_policy, aisle):
    outbound = [[] for _ in range(Levels)]
    inbound = [[] for _ in range(Levels)]
    to_notify = [[] for _ in range(Levels)]
    outbound_count = 0
    outbound_id = 0
    current_tier = 0

    while True:
        e_veh_to_buf =  [c_veh_to_buf[i].receive() if len(outbound[i]) < buf_cap else None for i in range(Levels)]
        e_lift_to_buf = [c_lift_to_buf[i].receive() if len(inbound[i]) < buf_cap else None for i in range(Levels)]
        e_lift_ready =   c_lift_ready.receive() if outbound_count > 0 else None
        e_buf_to_dem  = [c_buf_to_dem[i].send(to_notify[i][0]) if len(to_notify[i]) > 0 else None for i in range(Levels)]
        e_selected_tote = [c_selected_tote[i].receive() if len(inbound[i]) > 0 else None for i in range(Levels)]
        e_lift_position = c_lift_position.receive()

        selection = yield env.select(*(e_veh_to_buf + e_lift_to_buf + [e_lift_ready] + e_buf_to_dem + e_selected_tote +[e_lift_position]))

        for i in range(Levels):
            if selected(e_lift_ready):
                tier = lift_policies[lift_policy](outbound, current_tier)
                yield env.execute(c_next_tier.send(tier))
                yield env.execute(c_buf_to_lift.send(outbound[tier].pop(0)[0]))
                outbound_count -= 1
                yield env.execute(c_outbound_changed.send((aisle, tier)))
                break
            elif selected(e_lift_position):
                current_tier = selection
                break
            elif selected(e_veh_to_buf[i]):
                outbound[i].append((selection, outbound_id))
                outbound_count += 1
                outbound_id += 1
                break
            elif selected(e_lift_to_buf[i]):
                inbound[i].append(selection)
                to_notify[i].append(selection)
                break
            elif selected(e_buf_to_dem[i]):
                to_notify[i].pop(0)
                break
            elif selected(e_selected_tote[i]):
                x = selection
                inbound[x.tier].remove(x)
                yield env.execute(c_buf_to_veh[x.tier].send(x))
                yield env.execute(c_inbound_changed.send((aisle, x.tier)))
                break

@process
def Storage_Monitor(env, c_store_done, stats, stable_done, occupied_list):
    samples = []
    throughput = []

    while True:
        flow_time = yield env.execute(c_store_done.receive())
        samples.append(flow_time)
        throughput.append(len(samples) / env.now)

        stats['store_std'] = np.std(samples)
        stats['store_avg'] = np.mean(samples)
        stats['store_count'] = len(samples)

        if len(samples) >= min_samples:
            if np.std(throughput[-min_samples:]) < std_threshold:
                stable_done.succeed()

@process
def Retrieve_Monitor(env, c_retrieve_done, stats, stable_done, occupied_list):
    samples = []
    throughput = []

    while True:
        events = [c.receive() for c in c_retrieve_done]
        x = yield env.select(*events)

        flow_time = env.now - x.entrytime
        samples.append(flow_time)
        throughput.append(len(samples) / env.now)

        stats['retrieve_std'] = np.std(samples)
        stats['retrieve_avg'] = np.mean(samples)
        stats['retrieve_count'] = len(samples)

        if len(samples) >= min_samples:
            if np.std(throughput[-min_samples:]) < std_threshold:
                stable_done.succeed()

def model(Aisles, Levels, Columns, iat_retrieve, iat_store, buf_cap, store_policy, retrieve_policy, vehicle_policy, lift_policy):
    
    stats = {'store_avg': 0.0, 'store_std': 0.0, 'store_count': 0, 'retrieve_avg': 0.0, 'retrieve_std': 0.0, 'retrieve_count': 0}
    
    env = Environment()
    stable_done = env.event()

    # Warehouse initialization - odd columns occupied - 50% occupation
    coords = list(product(range(Aisles), range(Levels), range(Columns), [0, 1]))
    occupied_list = [c for c in coords if c[2] % 2 != 0]; random.shuffle(occupied_list)
    empty_list = [c for c in coords if c[2] % 2 == 0]; random.shuffle(empty_list)

    # First layer - Interface between global system and each Aisle
    c_retrieve_order = Channel(env)
    c_store_order = Channel(env)
    c_store_to_conv = [Channel(env) for _ in range(Aisles)]
    c_store_done = Channel(env)
    c_retrieve_to_dem = [[Channel(env) for _ in range(Levels)] for _ in range(Aisles)]
    c_retrieve_done = [Channel(env) for _ in range(Aisles)]
    c_inbound_changed = [Channel(env) for _ in range(Aisles)]
    c_outbound_changed = [Channel(env) for _ in range(Aisles)]

    Storage_Generator(env, c_store_order, iat_store, empty_list)
    Retrieval_Generator(env, c_retrieve_order, iat_retrieve, occupied_list)
    Storage_Controller(env, c_store_order, c_store_to_conv, empty_list, store_policy, c_inbound_changed, Aisles, Levels, buf_cap)
    Retrieval_Controller(env, c_retrieve_order, c_retrieve_to_dem, occupied_list, retrieve_policy, c_outbound_changed, Aisles, Levels, buf_cap)
    
    for a in range(Aisles):
        # Second layer - Interface between each Aisle and each Tier
        c_lift_to_buf = [Channel(env) for _ in range(Levels)]
        c_veh_to_buf = [Channel(env) for _ in range(Levels)]
        c_buf_to_veh = [Channel(env) for _ in range(Levels)]
        c_buf_to_dem = [Channel(env) for _ in range(Levels)]
        c_conv_to_lift = Channel(env)
        c_lift_to_conv = Channel(env)
        c_lift_ready = Channel(env)
        c_lift_position = Channel(env)
        c_next_tier = Channel(env)
        c_buf_to_lift = Channel(env)
        c_selected_tote = [Channel(env) for _ in range(Levels)]

        Conveyor(env, c_store_to_conv[a], c_conv_to_lift) # storage
        Conveyor(env, c_lift_to_conv, c_retrieve_done[a]) # retrieval
        Lift(env, c_lift_ready, c_next_tier, c_buf_to_lift, c_lift_to_conv, c_conv_to_lift, c_lift_to_buf, c_lift_position)
        Buffer(env, c_veh_to_buf, c_lift_ready, c_next_tier, c_buf_to_lift, c_lift_to_buf, c_buf_to_dem, c_buf_to_veh, c_selected_tote, buf_cap, Levels, c_inbound_changed[a], c_outbound_changed[a], c_lift_position, lift_policy, a)
        
        for t in range(Levels):
            # Third layer - Interface between each Tier and its vehicle
            c_dem_to_veh = Channel(env)
            Demand_Buffer(env, c_retrieve_to_dem[a][t], c_buf_to_dem[t], c_dem_to_veh, vehicle_policy)
            Vehicle(env, c_dem_to_veh, c_veh_to_buf[t], c_buf_to_veh[t], c_selected_tote[t], c_store_done, buf_cap, occupied_list, empty_list)
        
    Storage_Monitor(env, c_store_done, stats, stable_done, occupied_list)
    Retrieve_Monitor(env, c_retrieve_done, stats, stable_done, occupied_list)
    
    env.run(until=(stable_done))
    
    return stats

def experiment(Aisles, Levels, Columns, iat_retrieve, iat_store, buf_cap, store_policy, retrieve_policy, vehicle_policy, lift_policy):
    times.clear()

    start = time.time()
    result = model(Aisles, Levels, Columns, iat_retrieve, iat_store, buf_cap, store_policy, retrieve_policy, vehicle_policy, lift_policy)
    
    print(f"{Aisles},{Levels},{Columns} - {Aisles*Levels*Columns*2} - {buf_cap}, {store_policy},{retrieve_policy},{lift_policy},{vehicle_policy} - STORAGE avg: {result['store_avg']:.1f} s - RETRIEVAL avg: {result['retrieve_avg']:.1f} s - Sim. Time: {time.time() - start:.2f}s")

    return (result['store_avg'], result['retrieve_avg'])