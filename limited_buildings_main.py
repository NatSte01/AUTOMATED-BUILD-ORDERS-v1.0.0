
import heapq
import sys
import os
import pickle
import time
import random
import json
from dataclasses import dataclass, field, fields, asdict, MISSING
from collections import Counter
from typing import List, Dict, Any, Tuple, Set, Optional, TYPE_CHECKING, Union, Any, Type, TypeVar
from multiprocessing import Process, Queue, Event
import curses
import copy

if TYPE_CHECKING:
    import pygame

# Assuming curses is handled as before

# --- Constants ---
ACTION_BUILD = "build"
ACTION_UPGRADE = "upgrade"
ACTION_RECLAIM = "reclaim"

RESOURCE_METAL = "M"
RESOURCE_ENERGY = "E"
RESOURCE_BUILDPOWER = "Buildpower"

REQ_T1_COMMANDER = "T1_Commander"
REQ_T1_CONSTRUCTOR = "T1_Constructor"
REQ_T2_CONSTRUCTOR = "T2_Constructor"

# UNITS_DATA, UPGRADE_MAP, etc. assumed to be defined as in your previous complete code block
# For brevity, I'm omitting the full UNITS_DATA block here but it's needed.
# Make sure it's the same as the one you provided earlier.
UNITS_DATA: Dict[str, Dict[str, Any]] = {
    'EC':{'M':1, 'E':1250, 'Buildtime':27, 'Req':REQ_T1_COMMANDER, 'Input':{'E':70}, 'Output':{'M':1.0}, 'Name':'Energy Converter', 'Health':167.0, 'Speed':0.0, 'Tier':0, 'Type':'', 'BuildPower':0, 'EnergyMake':0.0, 'EnergyStorage':0, 'MetalMake':0.0, 'MetalStorage':0},
    'SC':{'M':150, 'E':0, 'Buildtime':28, 'Req':REQ_T1_COMMANDER, 'Output':{'E':20}, 'Name':'Solar Collector', 'Storage':{'E':50}, 'Health':355.0, 'Speed':0.0, 'Tier':0, 'Type':'', 'BuildPower':0, 'EnergyMake':0.0, 'MetalMake':0.0, 'MetalStorage':0},
    'ME':{'M':50, 'E':500, 'Buildtime':19, 'Req':REQ_T1_COMMANDER, 'Input':{'E':3}, 'Output':{'M':2.0}, 'Name':'Metal Extractor', 'Storage':{'M':50}, 'Health':194.0, 'Speed':0.0, 'Tier':0, 'Type':'CANBEUW', 'BuildPower':0, 'EnergyMake':0.0, 'EnergyStorage':0, 'MetalMake':0.0},
    'MS':{'M':300, 'E':590, 'Buildtime':30, 'Req':REQ_T1_COMMANDER, 'Name':'Metal Storage', 'Storage':{'M':3000}, 'Health':2100.0, 'Speed':0.0, 'Tier':0, 'Type':'', 'BuildPower':0, 'EnergyMake':0.0, 'EnergyStorage':0, 'MetalMake':0.0},
    'ES':{'M':175, 'E':1800, 'Buildtime':43, 'Req':REQ_T1_COMMANDER, 'Name':'Energy Storage', 'Storage':{'E':6000}, 'Health':2000.0, 'Speed':0.0, 'Tier':0, 'Type':'', 'BuildPower':0, 'EnergyMake':0.0, 'MetalMake':0.0, 'MetalStorage':0},
    'BL':{'M':620, 'E':1300, 'Buildtime':65, 'Req':REQ_T1_COMMANDER, 'Output':{RESOURCE_BUILDPOWER:100}, 'Name':'Bot Lab', 'Storage':{'E':100, 'M':100}, 'Reclaim':{'M':465, 'Time':32}, 'Health':2900.0, 'Speed':0.0, 'Tier':0, 'Type':'', 'BuildOptions':['corak', 'corck', 'corcrash', 'cornecro', 'corstorm', 'corthud'], 'EnergyMake':0.0, 'MetalMake':0.0},
    'VP':{'M':720, 'E':1800, 'Buildtime':72, 'Req':REQ_T1_COMMANDER, 'Output':{RESOURCE_BUILDPOWER:100}, 'Name':'Vehicle Plant', 'Storage':{'E':100, 'M':100}, 'Reclaim':{'M':540, 'Time':36}, 'Health':3000.0, 'Speed':0.0, 'Tier':0, 'Type':'', 'BuildOptions':['corcv', 'corfav', 'corgarp', 'corgator', 'corlevlr', 'cormist', 'cormlv', 'cormuskrat', 'corraid', 'corwolv'], 'EnergyMake':0.0, 'MetalMake':0.0},
    'AP':{'M':840, 'E':1350, 'Buildtime':72, 'Req':REQ_T1_COMMANDER, 'Output':{RESOURCE_BUILDPOWER:100}, 'Name':'Aircraft Plant', 'Storage':{'E':100, 'M':100}, 'Reclaim':{'M':630, 'Time':36}, 'Health':2150.0, 'Speed':0.0, 'Tier':0, 'Type':'', 'BuildOptions':['corbw', 'corca', 'corfink', 'corhvytrans', 'corshad', 'corvalk', 'corveng'], 'EnergyMake':0.0, 'MetalMake':0.0},
    'CB':{'M':120, 'E':1750, 'Buildtime':36, 'Req':'BL', 'Output':{RESOURCE_BUILDPOWER:85, 'E':7.0}, 'Name':'Construction Bot', 'Storage':{'E':50}, 'Health':660.0, 'Speed':34.5, 'Tier':0, 'Type':'', 'BuildOptions':['coradvsol', 'coralab', 'corap', 'cordl', 'cordrag', 'corerad', 'corestor', 'corexp', 'coreyes', 'corgeo', 'corhllt', 'corhlt', 'corhp', 'corjamt', 'corjuno', 'corlab', 'corllt', 'cormadsam', 'cormakr', 'cormaw', 'cormex', 'cormstor', 'cornanotc', 'corpun', 'corrad', 'corrl', 'corsolar', 'corsy', 'corvp', 'corwin'], 'MetalMake':0.0, 'MetalStorage':0},
    'CV':{'M':145, 'E':2100, 'Buildtime':42, 'Req':'VP', 'Output':{RESOURCE_BUILDPOWER:95, 'E':10.0}, 'Name':'Construction Vehicle', 'Storage':{'E':50}, 'Health':1430.0, 'Speed':51.0, 'Tier':0, 'Type':'', 'BuildOptions':['coradvsol', 'corap', 'coravp', 'cordl', 'cordrag', 'corerad', 'corestor', 'corexp', 'coreyes', 'corgeo', 'corhllt', 'corhlt', 'corhp', 'corjamt', 'corjuno', 'corlab', 'corllt', 'cormadsam', 'cormakr', 'cormaw', 'cormex', 'cormstor', 'cornanotc', 'corpun', 'corrad', 'corrl', 'corsolar', 'corsy', 'corvp', 'corwin'], 'MetalMake':0.0, 'MetalStorage':0},
    'CA':{'M':115, 'E':3200, 'Buildtime':84, 'Req':'AP', 'Output':{RESOURCE_BUILDPOWER:65, 'E':5.0}, 'Name':'Construction Aircraft', 'Storage':{'E':25}, 'Health':161.0, 'Speed':201.0, 'Tier':0, 'Type':'', 'BuildOptions':['coraap', 'coradvsol', 'corap', 'corasp', 'cordl', 'cordrag', 'corerad', 'corestor', 'corexp', 'coreyes', 'corfasp', 'corgeo', 'corhllt', 'corhlt', 'corhp', 'corjamt', 'corjuno', 'corlab', 'corllt', 'cormadsam', 'cormakr', 'cormaw', 'cormex', 'cormstor', 'cornanotc', 'corpun', 'corrad', 'corrl', 'corsolar', 'corsy', 'coruwgeo', 'corvp', 'corwin'], 'MetalMake':0.0, 'MetalStorage':0},
    'ASC':{'M':370, 'E':4000, 'Buildtime':82, 'Req':REQ_T1_CONSTRUCTOR, 'Input':{'E':75}, 'Output':{'E':75.0}, 'Name':'Advanced Solar Collector', 'Storage':{'E':100}, 'Health':1200.0, 'Speed':0.0, 'Tier':0, 'Type':'', 'BuildPower':0, 'MetalMake':0.0, 'MetalStorage':0},
    'CT':{'M':210, 'E':3200, 'Buildtime':53, 'Req':REQ_T1_CONSTRUCTOR, 'Output':{RESOURCE_BUILDPOWER:200}, 'Name':'Construction Turret', 'Health':560.0, 'Speed':0.0, 'Tier':0, 'Type':'', 'EnergyMake':0.0, 'EnergyStorage':0, 'MetalMake':0.0, 'MetalStorage':0},
    'ABL':{'M':2900, 'E':16000, 'Buildtime':168, 'Req':REQ_T1_CONSTRUCTOR, 'Output':{RESOURCE_BUILDPOWER:300}, 'Name':'Advanced Bot Lab', 'Storage':{'E':200, 'M':200}, 'Reclaim':{'M':2175, 'Time':84}, 'Health':4500.0, 'Speed':0.0, 'Tier':2, 'Type':'', 'BuildOptions':['coraak', 'corack', 'coramph', 'corcan', 'cordecom', 'corfast', 'corhrk', 'cormando', 'cormort', 'corpyro', 'corroach', 'corsktl', 'corspec', 'corspy', 'corsumo', 'cortermite', 'corvoyr'], 'EnergyMake':0.0, 'MetalMake':0.0},
    'AVP':{'M':2800, 'E':16000, 'Buildtime':185, 'Req':REQ_T1_CONSTRUCTOR, 'Output':{RESOURCE_BUILDPOWER:300}, 'Name':'Advanced Vehicle Plant', 'Storage':{'E':200, 'M':200}, 'Reclaim':{'M':2100, 'Time':92}, 'Health':5100.0, 'Speed':0.0, 'Tier':2, 'Type':'', 'BuildOptions':['coracv', 'corban', 'coreter', 'corgol', 'cormabm', 'cormart', 'corparrow', 'correap', 'corsala', 'corsent', 'cortrem', 'corvrad', 'corvroc'], 'EnergyMake':0.0, 'MetalMake':0.0},
    'AAP':{'M':3200, 'E':28000, 'Buildtime':207, 'Req':REQ_T1_CONSTRUCTOR, 'Output':{RESOURCE_BUILDPOWER:200}, 'Name':'Advanced Aircraft Plant', 'Storage':{'E':200, 'M':200}, 'Reclaim':{'M':2400, 'Time':103}, 'Health':3900.0, 'Speed':0.0, 'Tier':2, 'Type':'', 'BuildOptions':['coraca', 'corape', 'corawac', 'corcrwh', 'corhurc', 'corseah', 'cortitan', 'corvamp'], 'EnergyMake':0.0, 'MetalMake':0.0},
    'ACB':{'M':470, 'E':6900, 'Buildtime':97, 'Req':'ABL', 'Output':{RESOURCE_BUILDPOWER:190, 'E':14.0}, 'Name':'Advanced Construction Bot', 'Storage':{'E':100}, 'Health':1000.0, 'Speed':33.0, 'Tier':2, 'Type':'', 'BuildOptions':['corafus', 'corageo', 'coralab', 'corarad', 'corasp', 'corbhmth', 'corbuzz', 'cordoom', 'corflak', 'corfmd', 'corfort', 'corfus', 'corgant', 'corgate', 'corint', 'corlab', 'cormexp', 'cormmkr', 'cormoho', 'corscreamer', 'corsd', 'corshroud', 'corsilo', 'cortarg', 'cortoast', 'cortron', 'coruwadves', 'coruwadvms', 'corvipe'], 'MetalMake':0.0, 'MetalStorage':0},
    'ACV':{'M':580, 'E':7000, 'Buildtime':129, 'Req':'AVP', 'Output':{RESOURCE_BUILDPOWER:265, 'E':20.0}, 'Name':'Advanced Construction Vehicle', 'Storage':{'E':100}, 'Health':2150.0, 'Speed':49.5, 'Tier':2, 'Type':'', 'BuildOptions':['corafus', 'corageo', 'corarad', 'corasp', 'coravp', 'corbhmth', 'corbuzz', 'cordoom', 'corflak', 'corfmd', 'corfort', 'corfus', 'corgant', 'corgate', 'corint', 'cormexp', 'cormmkr', 'cormoho', 'corscreamer', 'corsd', 'corshroud', 'corsilo', 'cortarg', 'cortoast', 'cortron', 'coruwadves', 'coruwadvms', 'corvipe', 'corvp'], 'MetalMake':0.0, 'MetalStorage':0},
    'ACA':{'M':360, 'E':11000, 'Buildtime':180, 'Req':'AAP', 'Output':{RESOURCE_BUILDPOWER:105, 'E':10.0}, 'Name':'Advanced Construction Aircraft', 'Storage':{'E':50}, 'Health':205.0, 'Speed':181.5, 'Tier':2, 'Type':'', 'BuildOptions':['coraap', 'corafus', 'corageo', 'corap', 'corarad', 'corasp', 'corbhmth', 'corbuzz', 'cordoom', 'corfasp', 'corflak', 'corfmd', 'corfort', 'corfus', 'corgant', 'corgate', 'corint', 'cormexp', 'cormmkr', 'cormoho', 'corplat', 'corscreamer', 'corsd', 'corshroud', 'corsilo', 'cortarg', 'cortoast', 'cortron', 'coruwadves', 'coruwadvms', 'coruwageo', 'corvipe'], 'MetalMake':0.0, 'MetalStorage':0},
    'AEC':{'M':370, 'E':21000, 'Buildtime':313, 'Req':REQ_T2_CONSTRUCTOR, 'Input':{'E':600}, 'Output':{'M':10.3}, 'Name':'Advanced Energy Converter', 'Health':560.0, 'Speed':0.0, 'Tier':2, 'Type':'', 'BuildPower':0, 'EnergyMake':0.0, 'EnergyStorage':0, 'MetalMake':0.0, 'MetalStorage':0},
    'FR':{'M':4500, 'E':26000, 'Buildtime':754, 'Req':REQ_T2_CONSTRUCTOR, 'Output':{'E':1100.0}, 'Name':'Fusion Reactor', 'Storage':{'E':2500}, 'Health':5000.0, 'Speed':0.0, 'Tier':2, 'Type':'', 'BuildPower':0, 'MetalMake':0.0, 'MetalStorage':0},
    'AFR':{'M':9700, 'E':48000, 'Buildtime':3292, 'Req':REQ_T2_CONSTRUCTOR, 'Output':{'E':3000.0}, 'Name':'Advanced Fusion Reactor', 'Storage':{'E':9000}, 'Health':9400.0, 'Speed':0.0, 'Tier':2, 'Type':'', 'BuildPower':0, 'MetalMake':0.0, 'MetalStorage':0},
    'AME':{'M':640, 'E':8100, 'Buildtime':141, 'Req':REQ_T2_CONSTRUCTOR, 'Input':{'E':20}, 'Output':{'M':8.0}, 'Name':'Advanced Metal Extractor', 'Storage':{'M':600}, 'Health':3900.0, 'Speed':0.0, 'Tier':2, 'Type':'', 'BuildPower':0, 'EnergyMake':0.0, 'EnergyStorage':0, 'MetalMake':0.0},
    'AF':{'M':73, 'E':2800, 'Buildtime':3330, 'Req':'AP', 'Name':'Vengeance', 'Health':156.0, 'Speed':297.6, 'Tier':0, 'Type':'', 'BuildPower':0, 'EnergyMake':0.0, 'EnergyStorage':0, 'MetalMake':0.0, 'MetalStorage':0},
    'ICBM':{'M':7700, 'E':82000, 'Buildtime':1810, 'Req':REQ_T2_CONSTRUCTOR, 'Name':'Nuclear Silo', 'Health':6200.0, 'Speed':0.0, 'Tier':2, 'Type':'', 'BuildPower':0, 'EnergyMake':0.0, 'EnergyStorage':0, 'MetalMake':0.0, 'MetalStorage':0},
    'CORGOL':{'M':1650, 'E':22000, 'Buildtime':300, 'Req':'AVP', 'Name':'Corgol', 'Health':7800.0, 'Speed':40.5, 'Tier':2, 'Type':'', 'BuildPower':0, 'EnergyMake':0.0, 'EnergyStorage':0, 'MetalMake':0.0, 'MetalStorage':0},
    'CORRAD':{'M':60, 'E':630, 'Buildtime':11.4, 'Req':REQ_T2_CONSTRUCTOR, 'Name':'Corrad', 'Health':90.0, 'Speed':0.0, 'Tier':0, 'Type':'', 'BuildPower':0, 'EnergyMake':0.0, 'EnergyStorage':0, 'MetalMake':0.0, 'MetalStorage':0},
    'CORJAMT':{'M':115, 'E':5200, 'Buildtime':45.7, 'Req':REQ_T2_CONSTRUCTOR, 'Name':'Corjamt', 'Health':1070.0, 'Speed':0.0, 'Tier':0, 'Type':'', 'BuildPower':0, 'EnergyMake':0.0, 'EnergyStorage':0, 'MetalMake':0.0, 'MetalStorage':0},
    'CORMART':{'M':400, 'E':4400, 'Buildtime':65, 'Req':'AVP', 'Name':'Cormart', 'Health':1200.0, 'Speed':58.0, 'Tier':2, 'Type':'', 'BuildPower':0, 'EnergyMake':0.0, 'EnergyStorage':0, 'MetalMake':0.0, 'MetalStorage':0},
    'CORBAN':{'M':1000, 'E':23000, 'Buildtime':23.1, 'Req':'AVP', 'Name':'Corban', 'Health':2500.0, 'Speed':54.0, 'Tier':2, 'Type':'', 'BuildPower':0, 'EnergyMake':0.0, 'EnergyStorage':0, 'MetalMake':0.0, 'MetalStorage':0},    
}

UPGRADE_MAP: Dict[str, str] = {'ME': 'AME', 'EC': 'AEC', 'SC': 'ASC'}
REVERSE_UPGRADE_MAP: Dict[str, str] = {v: k for k, v in UPGRADE_MAP.items()}
T1_CONSTRUCTORS: Set[str] = {'CB', 'CV', 'CA', 'CT'}
T2_CONSTRUCTORS: Set[str] = {'ACB', 'ACV', 'ACA'}
ALL_CONSTRUCTORS = T1_CONSTRUCTORS | T2_CONSTRUCTORS
FACTORY_UNITS: Set[str] = {'CB', 'CV', 'CA', 'ACB', 'ACV', 'ACA'}
PRODUCING_FACTORIES: Set[str] = {'BL', 'VP', 'AP', 'ABL', 'AVP', 'AAP'}

ESSENTIAL_ECONOMY_UNITS: Set[str] = {'ME', 'SC', 'WT', 'MS', 'ES', 'EC', 'ASC', 'AEC', 'FR', 'AFR', 'AME'}
UTILITY_CONSTRUCTORS: Set[str] = {'CT', 'ACB', 'ACV', 'ACA'}

STARTING_METAL: int = 1000
STARTING_ENERGY: int = 1000
BASE_METAL_STORAGE: int = 1000
BASE_ENERGY_STORAGE: int = 1000
STARTING_M_INCOME: float = 0.0
STARTING_E_INCOME: float = 30.0
STARTING_BUILDPOWER: int = 300
MAX_METAL_EXTRACTORS: int = 6

NAME_TO_CODE: Dict[str, str] = {v['Name'].lower().replace(' ', '').replace('(', '').replace(')',''): k for k, v in UNITS_DATA.items()}
NAME_TO_CODE.update({k.lower(): k for k in UNITS_DATA.keys()})
NAME_TO_CODE.update({'solar': 'SC', 'mex': 'ME', 'econv': 'EC', 'fusion': 'FR'})

@dataclass(frozen=True, order=True)
class GameState: # Assuming GameState is defined as before
    time: float = field(compare=False, default=0.0)
    metal: float = field(compare=False, default=STARTING_METAL)
    energy: float = field(compare=False, default=STARTING_ENERGY)
    metal_income: float = field(compare=False, default=STARTING_M_INCOME)
    energy_income: float = field(compare=False, default=STARTING_E_INCOME)
    buildpower: int = field(compare=False, default=STARTING_BUILDPOWER)
    max_metal: int = field(compare=False, default=BASE_METAL_STORAGE)
    max_energy: int = field(compare=False, default=BASE_ENERGY_STORAGE)
    units: Tuple[Tuple[str, int], ...] = field(compare=False, default_factory=tuple)
    path: Tuple[str, ...] = field(compare=False, default_factory=tuple)
    total_metal_cost: float = field(compare=False, default=0.0)
    wasted_metal: float = field(compare=False, default=0.0)
    wasted_energy: float = field(compare=False, default=0.0)
    goal_step: int = field(compare=False, default=0)

    def get_unit_counts(self) -> Counter:
        return Counter(dict(self.units))

class GameLogic:
    # ... (other GameLogic methods: get_prereqs_for_unit, _recalculate_storage, etc. - KEEP LATEST VERSIONS) ...
    @staticmethod
    def get_prereqs_for_unit(unit_code: str, counts: Counter) -> Set[str]:
        prereqs: Set[str] = set()
        needed: Set[str] = {unit_code}
        processed: Set[str] = set() 

        while needed:
            u = needed.pop()
            if u in processed:
                continue
            processed.add(u)
            if u not in UNITS_DATA:
                continue 

            req_str: Optional[str] = UNITS_DATA[u].get('Req')
            if not req_str or req_str == REQ_T1_COMMANDER: 
                continue

            if req_str == REQ_T1_CONSTRUCTOR:
                if not any(c in counts and counts[c] > 0 for c in T1_CONSTRUCTORS):
                    prereqs.add('CB') 
                    needed.add('CB') 
            elif req_str == REQ_T2_CONSTRUCTOR:
                if not any(c in counts and counts[c] > 0 for c in T2_CONSTRUCTORS):
                    prereqs.add('ACB')
                    needed.add('ACB')
            elif req_str in UNITS_DATA: 
                if counts.get(req_str, 0) == 0:
                    prereqs.add(req_str)
                    needed.add(req_str) 
        return prereqs

    @staticmethod
    def _recalculate_storage(units_counter: Counter) -> Tuple[int, int]:
        metal_storage, energy_storage = BASE_METAL_STORAGE, BASE_ENERGY_STORAGE
        for unit, count in units_counter.items():
            if count > 0 and unit in UNITS_DATA and 'Storage' in UNITS_DATA[unit]:
                metal_storage += UNITS_DATA[unit]['Storage'].get(RESOURCE_METAL, 0) * count
                energy_storage += UNITS_DATA[unit]['Storage'].get(RESOURCE_ENERGY, 0) * count
        return metal_storage, energy_storage

    @staticmethod
    def _recalculate_economy(units_counter: Counter) -> Tuple[float, float, int]:
        metal_income, energy_income = STARTING_M_INCOME, STARTING_E_INCOME
        build_power = STARTING_BUILDPOWER 

        for unit, count in units_counter.items():
            if count == 0 or unit not in UNITS_DATA: 
                continue
            info = UNITS_DATA[unit]
            metal_income += info.get('Output', {}).get(RESOURCE_METAL, 0) * count
            energy_income += info.get('Output', {}).get(RESOURCE_ENERGY, 0) * count
            energy_income -= info.get('Input', {}).get(RESOURCE_ENERGY, 0) * count
            metal_income -= info.get('Input', {}).get(RESOURCE_METAL, 0) * count
            
            if unit in ALL_CONSTRUCTORS: 
                build_power += info.get('Output', {}).get(RESOURCE_BUILDPOWER, 0) * count
        return metal_income, energy_income, build_power

    @staticmethod
    def get_item_to_build(action_type: str, item_code: str) -> Optional[str]:
        if action_type == ACTION_UPGRADE:
            return UPGRADE_MAP.get(item_code)
        return item_code 

    @staticmethod
    def _simulate_action_time(state: GameState, action_type: str, item_code: str, metal_waste_bp_ratio: float, energy_waste_bp_ratio: float) -> Optional[float]:
        if action_type == ACTION_RECLAIM:
            current_buildpower = state.buildpower 
            if current_buildpower <= 0: return None
            if item_code in UNITS_DATA and 'Reclaim' in UNITS_DATA[item_code]:
                reclaim_time_data = UNITS_DATA[item_code]['Reclaim'].get('Time', float('inf'))
                if reclaim_time_data == float('inf') or reclaim_time_data <= 0: return state.time # Instant or invalid
                return state.time + (reclaim_time_data * 100.0 / current_buildpower)
            return None 

        target_unit_code = GameLogic.get_item_to_build(action_type, item_code)
        if not target_unit_code or target_unit_code not in UNITS_DATA: return None 

        unit_info = UNITS_DATA[target_unit_code]
        m_cost, e_cost = unit_info.get(RESOURCE_METAL, 0), unit_info.get(RESOURCE_ENERGY, 0)
        buildtime_points = unit_info.get('Buildtime', 0) * 100 

        if buildtime_points <= 0: return state.time # Instant build definition

        is_factory_build = target_unit_code in FACTORY_UNITS
        effective_buildpower = 100 if is_factory_build else state.buildpower
        
        if effective_buildpower <= 0: return None # No buildpower to build

        actual_seconds_to_build_at_full_speed = buildtime_points / effective_buildpower if effective_buildpower > 1e-9 else float('inf')
        if actual_seconds_to_build_at_full_speed == float('inf') : return None # Cannot build if BP is zero and time is needed

        m_drain_per_sec = m_cost / actual_seconds_to_build_at_full_speed if actual_seconds_to_build_at_full_speed > 1e-9 else float('inf')
        e_drain_per_sec = e_cost / actual_seconds_to_build_at_full_speed if actual_seconds_to_build_at_full_speed > 1e-9 else float('inf')
        
        if m_cost <= 1e-9 and e_cost <= 1e-9: 
             return state.time + actual_seconds_to_build_at_full_speed 

        time_to_m_zero = float('inf')
        if m_drain_per_sec > state.metal_income:
            deficit_m = m_drain_per_sec - state.metal_income
            if deficit_m > 1e-9: 
                time_to_m_zero = state.metal / deficit_m
        
        time_to_e_zero = float('inf')
        if e_drain_per_sec > state.energy_income:
            deficit_e = e_drain_per_sec - state.energy_income
            if deficit_e > 1e-9:
                time_to_e_zero = state.energy / deficit_e

        time_at_full_speed = min(time_to_m_zero, time_to_e_zero, actual_seconds_to_build_at_full_speed)
        
        if time_at_full_speed >= actual_seconds_to_build_at_full_speed - 1e-9: 
            return state.time + actual_seconds_to_build_at_full_speed

        m_consumed_full_speed = m_drain_per_sec * time_at_full_speed
        e_consumed_full_speed = e_drain_per_sec * time_at_full_speed
        build_progress_full_speed = effective_buildpower * time_at_full_speed 

        m_cost_remaining = m_cost - m_consumed_full_speed
        e_cost_remaining = e_cost - e_consumed_full_speed
        build_points_remaining = buildtime_points - build_progress_full_speed

        if build_points_remaining <= 1e-9: 
             return state.time + time_at_full_speed

        m_income_for_build = max(0, state.metal_income) 
        e_income_for_build = max(0, state.energy_income)

        if m_cost_remaining > 1e-9 and m_income_for_build < 1e-9: return None 
        if e_cost_remaining > 1e-9 and e_income_for_build < 1e-9: return None 

        bp_from_metal_income = (m_income_for_build / m_drain_per_sec) * effective_buildpower if m_drain_per_sec > 1e-9 else float('inf')
        bp_from_energy_income = (e_income_for_build / e_drain_per_sec) * effective_buildpower if e_drain_per_sec > 1e-9 else float('inf')
        
        throttled_buildpower = effective_buildpower
        if m_cost_remaining > 1e-9: 
            throttled_buildpower = min(throttled_buildpower, bp_from_metal_income)
        if e_cost_remaining > 1e-9: 
            throttled_buildpower = min(throttled_buildpower, bp_from_energy_income)

        if throttled_buildpower < 1e-9: return None 

        time_in_throttle = build_points_remaining / throttled_buildpower
        
        return state.time + time_at_full_speed + time_in_throttle

    @staticmethod
    def _get_next_state(state: GameState, action_type: str, item_code: str, new_time: float,
                        metal_waste_bp_ratio: float, energy_waste_bp_ratio: float,
                        energy_conversion_threshold_percentage: float,
                        energy_to_metal_conversion_rate: float
                        ) -> Optional[GameState]:
        time_delta = new_time - state.time
        if time_delta < -1e-9: return None

        new_units_counter = state.get_unit_counts()
        path_str_suffix = ""
        m_cost_of_action, e_cost_of_action = 0, 0 # Renamed for clarity
        new_total_metal_cost = state.total_metal_cost
        
        # --- Handle AME specific logic for unit changes BEFORE cost calculation ---
        # This is for the case where building AME reclaims an ME if slots are full
        # or upgrades an ME.
        original_item_code_for_action = item_code # Keep track of the user's intended action item
        target_unit_for_build_or_upgrade = GameLogic.get_item_to_build(action_type, item_code) # What's being built/upgraded to

        # --- AME Special Handling: Determine if it's an upgrade or a build-replacing-ME ---
        is_ame_upgrade_path = False
        is_ame_reclaim_then_build_path = False

        if action_type == ACTION_BUILD and target_unit_for_build_or_upgrade == 'AME':
            mex_count = new_units_counter.get('ME', 0)
            ame_count = new_units_counter.get('AME', 0)
            total_extractors = mex_count + ame_count

            if mex_count > 0: # Prefer to upgrade an existing ME
                is_ame_upgrade_path = True
                action_type = ACTION_UPGRADE # Change action type internally
                item_code = 'ME' # The item being acted upon is now ME
                target_unit_for_build_or_upgrade = 'AME' # Still AME
                path_str_suffix = f"Build AME (upgrades ME)" # Original intent was build AME
            elif total_extractors >= MAX_METAL_EXTRACTORS and mex_count > 0: # All slots full, no non-upgraded ME (shouldn't happen if prev check works)
                                                                            # This logic arm is more for "Build AME" when no ME to upgrade, but slots full and some ME *could* be reclaimed.
                                                                            # However, our upgrade path above is preferred.
                                                                            # Let's simplify: if we are building AME and ME exists, it's an upgrade.
                                                                            # If building AME, no ME exists, but slots are full of AMEs, then it's an error (handled by is_action_valid).
                                                                            # If building AME, no ME exists, slots full with *other* ME (not possible with current logic), then error.
                pass # This path will be tricky. is_action_valid should prevent invalid builds.
                     # The current is_action_valid for 'AME' might need to check if an ME exists for upgrade *if* slots are full.

        # Now, proceed with action cost and unit count changes based on potentially modified action_type/item_code
        if action_type == ACTION_BUILD or action_type == ACTION_UPGRADE:
            if not target_unit_for_build_or_upgrade or target_unit_for_build_or_upgrade not in UNITS_DATA: return None
            unit_info = UNITS_DATA[target_unit_for_build_or_upgrade]
            m_cost_of_action = unit_info.get(RESOURCE_METAL, 0)
            e_cost_of_action = unit_info.get(RESOURCE_ENERGY, 0)
            new_total_metal_cost += m_cost_of_action
            
            if action_type == ACTION_UPGRADE: # Handles normal upgrades and the AME upgrade path
                if item_code not in UNITS_DATA or new_units_counter.get(item_code, 0) <= 0: return None
                new_total_metal_cost -= UNITS_DATA[item_code].get(RESOURCE_METAL, 0) # Subtract cost of base unit
                new_units_counter[item_code] -= 1
                if new_units_counter[item_code] == 0:
                    del new_units_counter[item_code]
                new_units_counter[target_unit_for_build_or_upgrade] = new_units_counter.get(target_unit_for_build_or_upgrade, 0) + 1
                if not path_str_suffix: # If not already set by AME logic
                    path_str_suffix = f"Upgrade {item_code} to {target_unit_for_build_or_upgrade}"
            else: # Regular Build
                new_units_counter[target_unit_for_build_or_upgrade] = new_units_counter.get(target_unit_for_build_or_upgrade, 0) + 1
                if not path_str_suffix:
                    path_str_suffix = f"Build {target_unit_for_build_or_upgrade}"

        elif action_type == ACTION_RECLAIM:
            if item_code not in UNITS_DATA or new_units_counter.get(item_code, 0) <= 0 or 'Reclaim' not in UNITS_DATA[item_code]:
                return None
            reclaim_info = UNITS_DATA[item_code]['Reclaim']
            # Reclaim gives resources, so m_cost_of_action is negative
            m_cost_of_action = -reclaim_info.get(RESOURCE_METAL, 0)
            e_cost_of_action = -reclaim_info.get(RESOURCE_ENERGY, 0) # If reclaim gives energy
            
            # Adjust total_metal_cost: removing the original cost of the reclaimed unit
            new_total_metal_cost -= UNITS_DATA[item_code].get(RESOURCE_METAL,0) 
            
            new_units_counter[item_code] -= 1
            if new_units_counter[item_code] == 0:
                del new_units_counter[item_code]
            path_str_suffix = f"Reclaim {item_code}"
        
        # --- Resource Update Logic (Revised Waste Calculation) ---
        # 1. Calculate resources generated/converted during the time_delta
        generated_metal_this_step = state.metal_income * time_delta
        generated_energy_this_step = state.energy_income * time_delta
        
        # Base available before specific costs/gains of this action, but after general income
        current_metal_with_income = state.metal + generated_metal_this_step
        current_energy_with_income = state.energy + generated_energy_this_step

        # 2. Apply dynamic energy-to-metal conversion (if applicable)
        metal_from_conversion = 0
        energy_cost_of_conversion = 0
        if energy_to_metal_conversion_rate > 0 and \
           energy_conversion_threshold_percentage < 1.0 and \
           state.max_energy > 0: # Using OLD max_energy for threshold decision
            
            conversion_trigger_level = state.max_energy * energy_conversion_threshold_percentage
            
            if current_energy_with_income > conversion_trigger_level:
                energy_eligible_for_conversion = current_energy_with_income - conversion_trigger_level
                
                if energy_eligible_for_conversion > 1e-9:
                    # Conversion happens based on energy available *before* this action's E cost
                    metal_from_conversion = energy_eligible_for_conversion * energy_to_metal_conversion_rate
                    energy_cost_of_conversion = energy_eligible_for_conversion 

        # 3. Calculate net resources *after* income, conversion, and this action's specific costs/gains
        #    This is the *potential* amount of resources if there were no storage limits yet.
        potential_metal_after_all_effects = current_metal_with_income + metal_from_conversion - m_cost_of_action
        potential_energy_after_all_effects = current_energy_with_income - energy_cost_of_conversion - e_cost_of_action
        
        # 4. Recalculate storage based on the *new* unit counts (after the action is complete)
        max_m_after_action, max_e_after_action = GameLogic._recalculate_storage(new_units_counter)

        # 5. Determine final capped resources and calculate waste for this step
        #    Waste occurs if potential resources exceed the *new* storage limits.
        final_metal = min(max_m_after_action, max(0, potential_metal_after_all_effects))
        final_energy = min(max_e_after_action, max(0, potential_energy_after_all_effects))

        step_wasted_metal = max(0, potential_metal_after_all_effects - max_m_after_action)
        step_wasted_energy = max(0, potential_energy_after_all_effects - max_e_after_action)
        
        # Accumulate total waste
        new_wasted_metal = state.wasted_metal + step_wasted_metal
        new_wasted_energy = state.wasted_energy + step_wasted_energy
        # --- End of Revised Resource Update and Waste Calculation ---

        m_income_after_action, e_income_after_action, base_buildpower_after_action = GameLogic._recalculate_economy(new_units_counter)
        
        bonus_buildpower_from_metal = step_wasted_metal * metal_waste_bp_ratio # Use step waste for BP bonus
        bonus_buildpower_from_energy = step_wasted_energy * energy_waste_bp_ratio
        final_buildpower = base_buildpower_after_action + int(bonus_buildpower_from_metal + bonus_buildpower_from_energy)

        return GameState(
            time=new_time, metal=final_metal, energy=final_energy,
            metal_income=m_income_after_action, energy_income=e_income_after_action,
            buildpower=final_buildpower, 
            max_metal=max_m_after_action, max_energy=max_e_after_action,
            units=tuple(sorted(new_units_counter.items())), 
            path=state.path + (path_str_suffix,),
            total_metal_cost=new_total_metal_cost,
            wasted_metal=new_wasted_metal,
            wasted_energy=new_wasted_energy,
            goal_step=state.goal_step 
        )
    
    @staticmethod
    def is_action_valid(state: GameState, action_type: str, item_code: str) -> bool:
        counts = state.get_unit_counts()

        if action_type == ACTION_BUILD and item_code == 'AME': # Target is AME
            mex_count = counts.get('ME', 0)
            ame_count = counts.get('AME', 0)
            total_extractors = mex_count + ame_count

            if mex_count > 0: # If MEs exist, "build AME" implies upgrading one of them
                # Requirement for upgrade: T2 constructor
                if not any(counts.get(constructor_unit, 0) > 0 for constructor_unit in T2_CONSTRUCTORS):
                    return False # No T2 con to perform the implicit upgrade
                return True # Valid to "build AME" by upgrading an ME
            elif total_extractors < MAX_METAL_EXTRACTORS:
                # No MEs to upgrade, but free slots available to build AME directly
                # Requirement for direct AME build: T2 constructor
                if not any(counts.get(constructor_unit, 0) > 0 for constructor_unit in T2_CONSTRUCTORS):
                    return False
                return True # Valid to build AME in a new slot
            else: # No MEs to upgrade, and no free slots (all MAX_METAL_EXTRACTORS are AMEs)
                return False # Cannot build more AMEs

        # Standard ME build limit
        if action_type == ACTION_BUILD and item_code == 'ME':
            total_mex_count = counts.get('ME', 0) + counts.get('AME', 0)
            if total_mex_count >= MAX_METAL_EXTRACTORS:
                return False
        
        # Standard ME upgrade limit (can only upgrade if an ME exists)
        if action_type == ACTION_UPGRADE and item_code == 'ME': 
            if counts.get('ME', 0) == 0:
                 return False
            # Check if total extractors would exceed max *if this ME becomes an AME*
            # This is implicitly handled because an upgrade reduces ME count and increases AME count,
            # so total extractor count remains the same. The check is more about having an ME.

        if action_type == ACTION_RECLAIM:
            if item_code not in UNITS_DATA: return False 
            return counts.get(item_code, 0) > 0 and 'Reclaim' in UNITS_DATA[item_code]
            
        # Determine the actual unit being built or the target of an upgrade
        target_unit_code = GameLogic.get_item_to_build(action_type, item_code)
        if not target_unit_code or target_unit_code not in UNITS_DATA:
            return False 

        unit_info = UNITS_DATA[target_unit_code]

        if action_type == ACTION_UPGRADE:
            if item_code not in UNITS_DATA or counts.get(item_code, 0) == 0: # Must have base unit
                return False
            if UPGRADE_MAP.get(item_code) != target_unit_code: # Must be a valid upgrade path
                return False 
            # Specific check for upgrading ME to AME if all slots are somehow already AMEs
            # (This shouldn't happen if "build AME" logic is correct, but as a safeguard)
            if item_code == 'ME' and target_unit_code == 'AME':
                mex_count = counts.get('ME',0)
                ame_count = counts.get('AME',0)
                if mex_count == 0: return False # Cannot upgrade non-existent ME
                # If all slots are full of AMEs already, and we try to "upgrade ME", it means ME must exist.
                # The total count doesn't change, so MAX_METAL_EXTRACTORS isn't violated by the upgrade itself.
            
        req_str: Optional[str] = unit_info.get('Req')
        
        if not req_str: # Should not happen for valid units in UNITS_DATA
            return False 
        
        if req_str == REQ_T1_COMMANDER:
            return True 
        
        if req_str == REQ_T1_CONSTRUCTOR:
            return any(counts.get(constructor_unit, 0) > 0 for constructor_unit in T1_CONSTRUCTORS)
        
        if req_str == REQ_T2_CONSTRUCTOR: # e.g. for AME, ABL etc.
            return any(counts.get(constructor_unit, 0) > 0 for constructor_unit in T2_CONSTRUCTORS)
        
        if req_str in UNITS_DATA: # Prereq is another building/unit
            return counts.get(req_str, 0) > 0
        
        return False # Should not be reached if all cases covered

    @staticmethod
    def is_goal_step_complete(state: GameState, goal_sequence: List[Tuple[str, str, int]]) -> bool:
        if state.goal_step >= len(goal_sequence):
            # print(f"DEBUG: Goal step {state.goal_step} is >= len(goal_sequence) {len(goal_sequence)}. All goals complete.")
            return True 
        
        action, unit_code, target_count = goal_sequence[state.goal_step]
        counts = state.get_unit_counts()

        # print(f"DEBUG is_goal_step_complete: Current Goal Step {state.goal_step}")
        # print(f"DEBUG is_goal_step_complete: Goal: {action} {target_count}x {unit_code}")
        # print(f"DEBUG is_goal_step_complete: Current Counts: {counts}")

        completed = False
        if action == ACTION_BUILD:
            actual_count = counts.get(unit_code, 0)
            if unit_code in UPGRADE_MAP: 
                upgraded_form = UPGRADE_MAP[unit_code]
                actual_count += counts.get(upgraded_form, 0)
            completed = actual_count >= target_count
            # print(f"DEBUG is_goal_step_complete (BUILD): unit '{unit_code}', actual_count (incl. upgrades if T1 goal): {actual_count}, target: {target_count}, completed: {completed}")
        
        elif action == ACTION_UPGRADE: 
            upgraded_unit_code = UPGRADE_MAP.get(unit_code)
            if not upgraded_unit_code: 
                # print(f"DEBUG is_goal_step_complete (UPGRADE): Invalid upgrade target '{unit_code}'")
                return False 
            completed = counts.get(upgraded_unit_code, 0) >= target_count
            # print(f"DEBUG is_goal_step_complete (UPGRADE): base '{unit_code}' -> target_upgraded '{upgraded_unit_code}', actual_count: {counts.get(upgraded_unit_code, 0)}, target: {target_count}, completed: {completed}")

        elif action == ACTION_RECLAIM:
            completed = counts.get(unit_code, 0) <= target_count 
            # print(f"DEBUG is_goal_step_complete (RECLAIM): unit '{unit_code}', actual_count: {counts.get(unit_code, 0)}, target_max: {target_count}, completed: {completed}")
        
        # if completed:
        #     print(f"DEBUG: Goal step {state.goal_step} ({action} {unit_code}) COMPLETED.")
        # else:
        #     print(f"DEBUG: Goal step {state.goal_step} ({action} {unit_code}) NOT YET complete.")
        return completed
    
    @staticmethod
    def get_simulated_action_outcome(state: GameState, action_type: str, item_code: str,
                                    metal_waste_bp_ratio: float, energy_waste_bp_ratio: float,
                                    energy_conversion_threshold_percentage: float,
                                    energy_to_metal_conversion_rate: float
                                    ) -> Optional[GameState]:
        if not GameLogic.is_action_valid(state, action_type, item_code):
            return None

        # _simulate_action_time itself doesn't need the conversion parameters, as conversion
        # happens when resources are banked in _get_next_state.
        end_time = GameLogic._simulate_action_time(state, action_type, item_code, 
                                                   metal_waste_bp_ratio, energy_waste_bp_ratio)
        if end_time is None:
            return None
            
        return GameLogic._get_next_state(state, action_type, item_code, end_time, 
                                         metal_waste_bp_ratio, energy_waste_bp_ratio,
                                         energy_conversion_threshold_percentage, # Pass new param
                                         energy_to_metal_conversion_rate)

    @staticmethod
    def get_possible_actions(state: GameState, goal_sequence: List[Tuple[str, str, int]], allow_all_builds: bool = False) -> List[Tuple[str, str]]:
        """
        Generates a list of possible valid actions.
        - Focuses on current goal and its prerequisites.
        - Adds basic economy options to encourage exploration.
        - If allow_all_builds, considers all valid build/upgrade/reclaim actions.
        - Reclaim is NOT strategically forced during goal progression here; GA must discover it.
        """
        counts = state.get_unit_counts()
        potential_actions: Set[Tuple[str, str]] = set()
        build_targets: Set[str] = set()  # Units to build/upgrade_to

        all_primary_goals_met = state.goal_step >= len(goal_sequence)

        # 1. Actions for the current goal step (if goals are not yet met)
        if not all_primary_goals_met:
            current_g_action, current_g_unit, current_g_target_count = goal_sequence[state.goal_step]

            if current_g_action == ACTION_RECLAIM:
                if counts.get(current_g_unit, 0) > current_g_target_count and \
                GameLogic.is_action_valid(state, ACTION_RECLAIM, current_g_unit):
                    potential_actions.add((ACTION_RECLAIM, current_g_unit))

            elif current_g_action == ACTION_BUILD:
                build_targets.add(current_g_unit)
                build_targets.update(GameLogic.get_prereqs_for_unit(current_g_unit, counts))

            elif current_g_action == ACTION_UPGRADE:
                upgraded_form = UPGRADE_MAP.get(current_g_unit)
                if upgraded_form:
                    build_targets.add(upgraded_form)
                    build_targets.update(GameLogic.get_prereqs_for_unit(upgraded_form, counts))
                    if counts.get(current_g_unit, 0) == 0:
                        build_targets.add(current_g_unit)
                        build_targets.update(GameLogic.get_prereqs_for_unit(current_g_unit, counts))

        # 2. MODIFIED: Unconditionally add key economy options to explore more paths.
        #    This is "dumber" because it doesn't check if the economy is struggling.
        basic_economy_units = ['SC', 'ME', 'MS', 'ES']
        for unit_code in basic_economy_units:
            if GameLogic.is_action_valid(state, ACTION_BUILD, unit_code):
                potential_actions.add((ACTION_BUILD, unit_code))
        
        # Also consider building the first factory/constructor if none exist
        has_t1_constructor = any(counts.get(c, 0) > 0 for c in T1_CONSTRUCTORS)
        has_factory = any(counts.get(f, 0) > 0 for f in PRODUCING_FACTORIES)
        if not has_t1_constructor and not has_factory:
            if GameLogic.is_action_valid(state, ACTION_BUILD, 'BL'):
                potential_actions.add((ACTION_BUILD, 'BL'))
            if GameLogic.is_action_valid(state, ACTION_BUILD, 'VP'):
                potential_actions.add((ACTION_BUILD, 'VP'))


        # 3. Populate actions from build_targets (these are mostly goal-driven)
        for unit_to_target in build_targets:
            if unit_to_target not in UNITS_DATA: continue

            if GameLogic.is_action_valid(state, ACTION_BUILD, unit_to_target):
                potential_actions.add((ACTION_BUILD, unit_to_target))

            base_form = REVERSE_UPGRADE_MAP.get(unit_to_target)
            if base_form and counts.get(base_form, 0) > 0:
                if GameLogic.is_action_valid(state, ACTION_UPGRADE, base_form):
                    potential_actions.add((ACTION_UPGRADE, base_form))

        # 4. If allow_all_builds is True, or if goals are met, consider all valid actions
        if allow_all_builds or all_primary_goals_met:
            for unit_code_iter in UNITS_DATA.keys():
                if GameLogic.is_action_valid(state, ACTION_BUILD, unit_code_iter):
                    potential_actions.add((ACTION_BUILD, unit_code_iter))
                if unit_code_iter in UPGRADE_MAP and counts.get(unit_code_iter, 0) > 0:
                    if GameLogic.is_action_valid(state, ACTION_UPGRADE, unit_code_iter):
                        potential_actions.add((ACTION_UPGRADE, unit_code_iter))

            goal_units_final_state = {UPGRADE_MAP.get(g_u, g_u) if g_a == ACTION_UPGRADE else g_u
                                    for g_a, g_u, _ in goal_sequence if g_a != ACTION_RECLAIM}
            units_to_preserve_if_goals_not_met = goal_units_final_state | UTILITY_CONSTRUCTORS | ESSENTIAL_ECONOMY_UNITS

            for unit_owned, num_owned in counts.items():
                if num_owned > 0 and GameLogic.is_action_valid(state, ACTION_RECLAIM, unit_owned):
                    if all_primary_goals_met:
                        if unit_owned not in (goal_units_final_state | UTILITY_CONSTRUCTORS | ESSENTIAL_ECONOMY_UNITS):
                            potential_actions.add((ACTION_RECLAIM, unit_owned))
                    elif allow_all_builds:
                        is_current_reclaim_goal = False
                        if not all_primary_goals_met and goal_sequence[state.goal_step][0] == ACTION_RECLAIM and goal_sequence[state.goal_step][1] == unit_owned:
                            is_current_reclaim_goal = True
                        if not is_current_reclaim_goal and unit_owned not in units_to_preserve_if_goals_not_met:
                            potential_actions.add((ACTION_RECLAIM, unit_owned))

        # Final filter for validity (redundant but safe) and fallback
        final_actions = [a for a in potential_actions if GameLogic.is_action_valid(state, *a)]
        if not final_actions and not all_primary_goals_met:
            if GameLogic.is_action_valid(state, ACTION_BUILD, 'SC'): final_actions.append((ACTION_BUILD, 'SC'))
            elif GameLogic.is_action_valid(state, ACTION_BUILD, 'ME'): final_actions.append((ACTION_BUILD, 'ME'))

        return final_actions
    

# Generic type variable for the class itself, used for type hinting classmethods
T_Config = TypeVar('T_Config', bound='GeneticAlgorithmConfig')

@dataclass
class GeneticAlgorithmConfig:
    """
    Configuration settings for the Genetic Algorithm.
    
    This class uses dataclasses for clean, type-hinted, and self-documenting
    configuration management. It includes methods for serialization to and from
    dictionaries and JSON files, and performs validation on initialization.
    """
    
    # --- GA Core Parameters ---
    population_size: int = 150
    base_mutation_rate: float = 0.50
    mutation_decay: float = 0.99
    elitism_count: int = 5
    tournament_size: int = 20
    crossover_type: str = 'one_point'
    max_chromosome_len: int = 100

    # --- Speciation and Diversity Control ---
    stagnation_limit: int = 40
    catastrophe_limit: int = 80
    hyper_mutation_rate: float = 0.95 # Note: Rate seems very high, ensure this is intended.

    # --- Chromosome Generation Control ---
    heuristic_seed_count: int = 50
    stop_chromosome_generation_after_goals_prob: float = 0.99
    max_post_goal_actions_in_chromosome: int = 0
    
    # --- Fitness Function Coefficients ---
    time_score_factor: float = 100000.0
    path_length_penalty_factor: float = 0.0
    total_metal_cost_penalty_factor: float = -1000
    wasted_metal_penalty_factor: float = 1000.0
    wasted_energy_penalty_factor: float = 0.0
    incomplete_goal_base_penalty: float = 100000.0
    incomplete_goal_step_penalty: float = 100000.0
    unused_reclaimable_penalty_factor: float = 0.001
    unused_non_reclaimable_penalty_factor: float = 0.002

    # --- Fitness Bonuses ---
    min_metal_income_for_bonus: float = 0.0
    min_energy_income_for_bonus: float = 0.0
    final_positive_income_bonus_factor: float = 100.0
    low_waste_metal_threshold: float = 0.0
    low_waste_energy_threshold: float = 0.0
    low_waste_bonus_amount: float = 1.0

    # --- Simulation Parameters (passed to GameLogic) ---
    metal_waste_to_bp_ratio: float = 0.01
    energy_waste_to_bp_ratio: float = 0.01
    energy_conversion_threshold_percentage: float = 0.80
    energy_to_metal_conversion_rate: float = 0.01

    def __post_init__(self):
        """Perform validation after the object is initialized."""
        if not 0.0 <= self.base_mutation_rate <= 1.0:
            raise ValueError("base_mutation_rate must be between 0.0 and 1.0")
        if self.elitism_count >= self.population_size:
            raise ValueError("elitism_count must be smaller than population_size")
        if self.tournament_size > self.population_size:
            raise ValueError("tournament_size cannot be larger than population_size")

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the configuration to a dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls: Type[T_Config], data: Dict[str, Any]) -> T_Config:
        """
        Creates a configuration instance from a dictionary, ignoring extraneous keys.
        This allows loading from older or newer config files without errors.
        """
        # Get the set of field names defined in the dataclass
        known_keys = {f.name for f in fields(cls)}
        
        # Filter the input dictionary to only include keys that are actual fields in the class
        filtered_data = {k: v for k, v in data.items() if k in known_keys}
        
        # Unpack the filtered dictionary into the constructor.
        # This is the idiomatic way to create the instance with the loaded data.
        return cls(**filtered_data)

    def save_to_json(self, file_path: str):
        """Saves the configuration to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load_from_json(cls: Type[T_Config], file_path: str) -> T_Config:
        """Loads configuration from a JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
class GeneticAlgorithmRunner:
    def __init__(self, config: GeneticAlgorithmConfig, goal_sequence: List[Tuple[str, str, int]],
                 results_queue: 'Queue', stop_event: Event, pause_event: Event, worker_id: int):
            
            # Store a pristine copy of the original config for resets
            self.initial_config = copy.deepcopy(config) 
            # Each worker gets its own mutable copy of the config
            self.config = copy.deepcopy(config) 

            self.goal_sequence = goal_sequence
            self.results_queue = results_queue
            self.stop_event = stop_event
            self.pause_event = pause_event
            self.worker_id = worker_id
            
            random.seed(os.getpid() * time.time() + worker_id)

            self.time_improvement_tracker = {'last_best_time_for_factor_adj': float('inf'), 'generations_since_time_improvement': 0}


    def calculate_efficiency_score(self, state: Optional[GameState], current_config: GeneticAlgorithmConfig) -> float:
        if not state: return float('inf')

        time_score = state.time * current_config.time_score_factor
        path_length_penalty = len(state.path) * current_config.path_length_penalty_factor

        goal_completed = state.goal_step >= len(self.goal_sequence)

        if not goal_completed:
            final_score = time_score # Make it the absolute primary
            final_score += path_length_penalty * 0.001 # Very small tie-breaker
            final_score += state.total_metal_cost * current_config.total_metal_cost_penalty_factor * 0.01 # Smaller
            final_score += (state.wasted_metal * current_config.wasted_metal_penalty_factor * 0.01 +
                            state.wasted_energy * current_config.wasted_energy_penalty_factor * 0.01) # Smaller
            return final_score
        
        # --- GOALS MET ---
        final_score = time_score + path_length_penalty
        final_score += state.total_metal_cost * current_config.total_metal_cost_penalty_factor
        final_score += (state.wasted_metal * current_config.wasted_metal_penalty_factor +
                        state.wasted_energy * current_config.wasted_energy_penalty_factor)
        
        goal_units_set = set()
        for action, unit_base, _ in self.goal_sequence:
            if action == ACTION_BUILD: goal_units_set.add(unit_base)
            elif action == ACTION_UPGRADE and unit_base in UPGRADE_MAP:
                goal_units_set.add(UPGRADE_MAP[unit_base])

        units_to_keep = goal_units_set | UTILITY_CONSTRUCTORS
        current_counts = state.get_unit_counts()
        for unit_code, count in current_counts.items():
            if count > 0 and unit_code in ESSENTIAL_ECONOMY_UNITS:
                 info = UNITS_DATA.get(unit_code,{})
                 m_out = info.get('Output',{}).get(RESOURCE_METAL,0); e_out = info.get('Output',{}).get(RESOURCE_ENERGY,0)
                 m_in = info.get('Input',{}).get(RESOURCE_METAL,0); e_in = info.get('Input',{}).get(RESOURCE_ENERGY,0)
                 if (m_out - m_in > 0.01) or (e_out - e_in > 0.01):
                     units_to_keep.add(unit_code)

        unused_unit_penalty = 0
        for unit, count_val in current_counts.items():
            if count_val > 0 and unit not in units_to_keep:
                unit_data = UNITS_DATA.get(unit, {})
                unit_metal_cost = unit_data.get(RESOURCE_METAL, 0)
                if 'Reclaim' in unit_data:
                    penalty_factor = current_config.unused_reclaimable_penalty_factor
                else:
                    penalty_factor = current_config.unused_non_reclaimable_penalty_factor
                unused_unit_penalty += (penalty_factor * unit_metal_cost * count_val)
        final_score += unused_unit_penalty
        
        income_bonus = 0.0
        if state.metal_income > current_config.min_metal_income_for_bonus and \
           state.energy_income > current_config.min_energy_income_for_bonus:
            income_bonus_raw = (state.metal_income * 0.1 + state.energy_income * 0.01)
            income_bonus = income_bonus_raw * current_config.final_positive_income_bonus_factor
        final_score -= income_bonus

        low_waste_bonus = 0.0
        if state.wasted_metal < current_config.low_waste_metal_threshold and \
           state.wasted_energy < current_config.low_waste_energy_threshold:
            low_waste_bonus = current_config.low_waste_bonus_amount
        final_score -= low_waste_bonus

        return final_score

# Inside GeneticAlgorithmRunner class

    def _generate_random_chromosome(self, use_heuristic_start: bool = False) -> List[Tuple[str, str]]:
         state = GameState()
         chromosome: List[Tuple[str, str]] = []
         post_goal_actions_added = 0

         if use_heuristic_start and self.goal_sequence and self.config.heuristic_seed_count > 0:
             h_state = GameState()
             h_goal_step = 0
             max_h_actions = self.config.max_chromosome_len // 2

             for _ in range(max_h_actions):
                 if h_goal_step >= len(self.goal_sequence) or len(chromosome) >= max_h_actions: break

                 h_goals_view = self.goal_sequence[h_goal_step:]
                 if not h_goals_view: break

                 poss_h_actions = GameLogic.get_possible_actions(h_state, h_goals_view, allow_all_builds=False)
                 if not poss_h_actions: break

                 chosen_h_action = random.choice(poss_h_actions)

                 # This is the call site indicated by the traceback (around line 776)
                 next_h_s = GameLogic.get_simulated_action_outcome(
                     h_state, *chosen_h_action,
                     self.config.metal_waste_to_bp_ratio,
                     self.config.energy_waste_to_bp_ratio,
                     self.config.energy_conversion_threshold_percentage, # ARGUMENT PRESENT
                     self.config.energy_to_metal_conversion_rate        # ARGUMENT PRESENT
                 )
                 if next_h_s is None: break

                 chromosome.append(chosen_h_action)
                 h_state = next_h_s

                 # ... (rest of heuristic section) ...
                 temp_h_state_for_goal_check = GameState(**{**vars(h_state), 'goal_step':0}) # type: ignore
                 temp_h_goal_step_progress = 0
                 while GameLogic.is_goal_step_complete(temp_h_state_for_goal_check, self.goal_sequence[h_goal_step : h_goal_step + temp_h_goal_step_progress + 1]) and \
                       temp_h_goal_step_progress < len(self.goal_sequence[h_goal_step:]):
                     temp_h_state_for_goal_check = GameState(**{**vars(temp_h_state_for_goal_check), 'goal_step': temp_h_state_for_goal_check.goal_step + 1}) # type: ignore
                     temp_h_goal_step_progress +=1
                 if temp_h_goal_step_progress > 0 and GameLogic.is_goal_step_complete(h_state, self.goal_sequence[h_goal_step : h_goal_step + 1]):
                      h_goal_step +=1


             current_eval_state = GameState()
             for action_in_prefix in chromosome:
                 next_eval_s = GameLogic.get_simulated_action_outcome(
                     current_eval_state, *action_in_prefix,
                     self.config.metal_waste_to_bp_ratio,
                     self.config.energy_waste_to_bp_ratio,
                     self.config.energy_conversion_threshold_percentage, # ARGUMENT PRESENT
                     self.config.energy_to_metal_conversion_rate        # ARGUMENT PRESENT
                 )
                 if not next_eval_s:
                     chromosome = []; current_eval_state = GameState(); break
                 current_eval_state = next_eval_s
                 while GameLogic.is_goal_step_complete(current_eval_state, self.goal_sequence) and \
                     current_eval_state.goal_step < len(self.goal_sequence):
                     current_eval_state = GameState(**{**vars(current_eval_state), 'goal_step': current_eval_state.goal_step + 1}) # type: ignore
             state = current_eval_state

         for _ in range(self.config.max_chromosome_len - len(chromosome)):
             all_primary_goals_met = state.goal_step >= len(self.goal_sequence)

             if all_primary_goals_met:
                 if post_goal_actions_added >= self.config.max_post_goal_actions_in_chromosome: break
                 if random.random() < self.config.stop_chromosome_generation_after_goals_prob: break
                 possible_actions = GameLogic.get_possible_actions(state, self.goal_sequence, allow_all_builds=True)
                 if possible_actions : post_goal_actions_added +=1
             else:
                 possible_actions = GameLogic.get_possible_actions(state, self.goal_sequence, allow_all_builds=False)
                 if not possible_actions:
                     possible_actions = GameLogic.get_possible_actions(state, self.goal_sequence, allow_all_builds=True)

             if not possible_actions: break
             action_to_add = random.choice(possible_actions)
             next_s = GameLogic.get_simulated_action_outcome(
                 state, *action_to_add,
                 self.config.metal_waste_to_bp_ratio,
                 self.config.energy_waste_to_bp_ratio,
                 self.config.energy_conversion_threshold_percentage, # ARGUMENT PRESENT
                 self.config.energy_to_metal_conversion_rate        # ARGUMENT PRESENT
             )
             if next_s is None: continue
             chromosome.append(action_to_add)
             state = next_s
             while GameLogic.is_goal_step_complete(state, self.goal_sequence) and \
                 state.goal_step < len(self.goal_sequence):
                 state = GameState(**{**vars(state), 'goal_step': state.goal_step + 1}) # type: ignore
         return chromosome
    
    def _crossover_chromosomes(self, parent1: List[Tuple[str,str]], parent2: List[Tuple[str,str]]) -> Tuple[List[Tuple[str,str]], List[Tuple[str,str]]]:
        p1, p2 = list(parent1), list(parent2); len1, len2 = len(p1), len(p2)
        child1, child2 = list(p1), list(p2) 
        if not p1 or not p2 or min(len1,len2) < 2 : return child1, child2
        if self.config.crossover_type == 'one_point':
            point = random.randint(1, min(len1, len2) -1)
            child1, child2 = p1[:point] + p2[point:], p2[:point] + p1[point:]
        elif self.config.crossover_type == 'two_point':
            if min(len1, len2) > 2: 
                pt1, pt2 = sorted(random.sample(range(1, min(len1, len2)), 2))
                child1, child2 = p1[:pt1] + p2[pt1:pt2] + p1[pt2:], p2[:pt1] + p1[pt1:pt2] + p2[pt2:]
            else: 
                 point = random.randint(1, min(len1, len2) -1) if min(len1,len2)>1 else 0
                 if point > 0: child1, child2 = p1[:point] + p2[point:], p2[:point] + p1[point:]
        elif self.config.crossover_type == 'uniform':
            c1, c2 = [], []
            for i in range(max(len1, len2)):
                g1_p1 = p1[i] if i < len1 else None; g1_p2 = p2[i] if i < len2 else None
                g2_p1 = p1[i] if i < len1 else None; g2_p2 = p2[i] if i < len2 else None
                if random.random() < 0.5:
                    if g1_p1: c1.append(g1_p1)
                    elif g1_p2: c1.append(g1_p2) 
                    if g2_p2: c2.append(g2_p2)
                    elif g2_p1: c2.append(g2_p1)
                else:
                    if g1_p2: c1.append(g1_p2)
                    elif g1_p1: c1.append(g1_p1)
                    if g2_p1: c2.append(g2_p1)
                    elif g2_p2: c2.append(g2_p2)
            child1, child2 = c1, c2
        return child1[:self.config.max_chromosome_len], child2[:self.config.max_chromosome_len]

    def _mutate_chromosome(self, chromosome: List[Tuple[str, str]], current_mutation_rate_for_logic: float) -> List[Tuple[str, str]]:
        if not chromosome:
            return []
        
        mut_chromo = list(chromosome)
        idx_mut = random.randint(0, len(mut_chromo))
        temp_s = GameState()

        for i in range(idx_mut):
            if i >= len(mut_chromo): break
            action_tuple = mut_chromo[i]
            # === THIS CALL SITE IN _mutate_chromosome ALSO NEEDS UPDATING ===
            next_t_s = GameLogic.get_simulated_action_outcome(
                temp_s, *action_tuple,
                self.config.metal_waste_to_bp_ratio,
                self.config.energy_waste_to_bp_ratio,
                self.config.energy_conversion_threshold_percentage, # ADD THIS
                self.config.energy_to_metal_conversion_rate        # ADD THIS
            )
            if next_t_s is None:
                return list(chromosome)
            temp_s = next_t_s
            while GameLogic.is_goal_step_complete(temp_s, self.goal_sequence) and \
                  temp_s.goal_step < len(self.goal_sequence):
                temp_s = GameState(**{**vars(temp_s), 'goal_step': temp_s.goal_step + 1}) #type: ignore
        # ... rest of _mutate_chromosome ...
        goals_met_b4_mut = temp_s.goal_step >= len(self.goal_sequence)
        force_explore = current_mutation_rate_for_logic >= self.config.hyper_mutation_rate * 0.9
        poss_acts_at_mut = GameLogic.get_possible_actions(temp_s, self.goal_sequence,
                                                        allow_all_builds=(goals_met_b4_mut or force_explore))
        mutation_type = random.randint(1, 4)
        if mutation_type == 1:
            if idx_mut < len(mut_chromo) and mut_chromo:
                del mut_chromo[idx_mut]
        elif mutation_type == 2:
            if len(mut_chromo) < self.config.max_chromosome_len and poss_acts_at_mut:
                can_insert_post_goal = not (goals_met_b4_mut and \
                                            self.config.max_post_goal_actions_in_chromosome == 0 and \
                                            random.random() < 0.7)
                if can_insert_post_goal:
                    mut_chromo.insert(idx_mut, random.choice(poss_acts_at_mut))
        elif mutation_type == 3:
            if idx_mut < len(mut_chromo) and mut_chromo and poss_acts_at_mut:
                mut_chromo[idx_mut] = random.choice(poss_acts_at_mut)
        elif mutation_type == 4:
            if len(mut_chromo) < self.config.max_chromosome_len and poss_acts_at_mut:
                can_insert_post_goal = not (goals_met_b4_mut and \
                                            self.config.max_post_goal_actions_in_chromosome == 0 and \
                                            random.random() < 0.7)
                if can_insert_post_goal:
                    mut_chromo.insert(idx_mut, random.choice(poss_acts_at_mut))
        return mut_chromo[:self.config.max_chromosome_len]
    
    def run(self):
        try:
            population = []
            num_heuristic_to_generate = min(self.config.heuristic_seed_count, self.config.population_size)
            for _ in range(num_heuristic_to_generate):
                if self.stop_event.is_set(): break
                population.append(self._generate_random_chromosome(use_heuristic_start=True))
            
            if not self.stop_event.is_set():
                num_random_to_generate = max(0, self.config.population_size - len(population))
                for _ in range(num_random_to_generate):
                    if self.stop_event.is_set(): break
                    population.append(self._generate_random_chromosome())
            
            if not population and self.config.population_size > 0 and not self.stop_event.is_set():
                raise RuntimeError(f"Worker {self.worker_id}: Population is empty after init.")

            best_solution_local: Optional[GameState] = None
            best_fitness_local = float('inf')
            stagnation_counter = 0
            current_mutation_rate = self.config.base_mutation_rate # Initialized in run's scope
            generation = 0

            self.time_improvement_tracker = {'last_best_time_for_factor_adj': float('inf'), 'generations_since_time_improvement': 0}

            while not self.stop_event.is_set():
                if self.pause_event.is_set():
                    initial_pause_sent = False
                    if self.results_queue and not initial_pause_sent:
                        try:
                            self.results_queue.put({"type": "status", "worker_id": self.worker_id, "message": f"W{self.worker_id} Paused"})
                            initial_pause_sent = True
                        except Exception: pass 
                    while self.pause_event.is_set() and not self.stop_event.is_set():
                        time.sleep(0.5)
                    if self.stop_event.is_set(): break
                    if self.results_queue: 
                        try:
                            self.results_queue.put({"type": "status", "worker_id": self.worker_id, "message": f"W{self.worker_id} Resuming..."})
                        except Exception: pass

                evaluated_population: List[Tuple[float, GameState, List[Tuple[str,str]]]] = []
                for chromo_idx, chromo in enumerate(population):
                    if self.stop_event.is_set(): break
                    final_state = self._simulate_chromosome(chromo)
                    if final_state:
                        fitness = self.calculate_efficiency_score(final_state, self.config) 
                        evaluated_population.append((fitness, final_state, chromo))
                
                if self.stop_event.is_set(): break

                if not evaluated_population:
                    # ... (re-population logic as before) ...
                    stagnation_counter +=1
                    generation += 1
                    continue

                evaluated_population.sort(key=lambda x: x[0])
                current_best_fitness_in_gen, current_best_state_in_gen, _ = evaluated_population[0]
                
                # --- Dynamic time_score_factor adjustment ---
                if current_best_state_in_gen and current_best_state_in_gen.goal_step >= len(self.goal_sequence):
                    new_best_time_this_gen = current_best_state_in_gen.time
                    if new_best_time_this_gen < self.time_improvement_tracker['last_best_time_for_factor_adj']:
                        self.time_improvement_tracker['last_best_time_for_factor_adj'] = new_best_time_this_gen
                        self.time_improvement_tracker['generations_since_time_improvement'] = 0
                    else:
                        self.time_improvement_tracker['generations_since_time_improvement'] += 1

                    TARGET_TIME_IMPROVEMENT_WINDOW = self.initial_config.stagnation_limit // 2 
                    TIME_FACTOR_INCREMENT = self.initial_config.time_score_factor * 0.05 
                    MAX_TIME_FACTOR = self.initial_config.time_score_factor * 5 

                    if (self.time_improvement_tracker['generations_since_time_improvement'] >= TARGET_TIME_IMPROVEMENT_WINDOW and
                        stagnation_counter < self.initial_config.stagnation_limit // 2 and 
                        self.config.time_score_factor < MAX_TIME_FACTOR):
                        
                        original_factor = self.config.time_score_factor
                        self.config.time_score_factor += TIME_FACTOR_INCREMENT
                        self.config.time_score_factor = min(self.config.time_score_factor, MAX_TIME_FACTOR)
                        self.time_improvement_tracker['generations_since_time_improvement'] = 0 
                        
                        if self.results_queue and abs(self.config.time_score_factor - original_factor) > 0.01:
                            self.results_queue.put({
                                "type": "status", "worker_id": self.worker_id,
                                "message": f"W{self.worker_id} G{generation}: Time stagn. Inc time_factor to {self.config.time_score_factor:.1f}"
                            })
                # --- End dynamic time_score_factor adjustment ---

                if current_best_fitness_in_gen < best_fitness_local:
                    best_fitness_local = current_best_fitness_in_gen
                    best_solution_local = current_best_state_in_gen
                    stagnation_counter = 0
                    current_mutation_rate = self.config.base_mutation_rate 
                    if self.results_queue:
                        self.results_queue.put({"type": "solution", "solution": best_solution_local, "generation": generation, "worker_id": self.worker_id, "fitness": best_fitness_local})
                else:
                    stagnation_counter += 1

                # Update current_mutation_rate based on stagnation/catastrophe
                if stagnation_counter >= self.config.catastrophe_limit:
                    if self.results_queue: self.results_queue.put({"type": "status", "worker_id": self.worker_id, "message": f"W{self.worker_id} G{generation}: Catastrophe! Reset."})
                    self.config = copy.deepcopy(self.initial_config) 
                    self.time_improvement_tracker = {'last_best_time_for_factor_adj': float('inf'), 'generations_since_time_improvement': 0}
                    # ... (population reset for catastrophe as before) ...
                    num_elites_cat = min(self.config.elitism_count, len(evaluated_population)) # Ensure this is defined
                    elite_chromos = [c for _,_,c in evaluated_population[:num_elites_cat]]
                    seeds_to_add = []
                    num_seeds_cat = min(self.config.heuristic_seed_count * 2, self.config.population_size - len(elite_chromos))
                    if self.config.heuristic_seed_count > 0 and num_seeds_cat > 0:
                        for _ in range(num_seeds_cat):
                            if self.stop_event.is_set(): break
                            seeds_to_add.append(self._generate_random_chromosome(use_heuristic_start=True))
                    if self.stop_event.is_set(): break
                    randoms_needed = max(0, self.config.population_size - len(elite_chromos) - len(seeds_to_add))
                    randoms_to_add = []
                    for _ in range(randoms_needed):
                        if self.stop_event.is_set(): break
                        randoms_to_add.append(self._generate_random_chromosome())
                    if self.stop_event.is_set(): break
                    population = (elite_chromos + seeds_to_add + randoms_to_add)[:self.config.population_size]
                    if not population and self.config.population_size > 0 and not self.stop_event.is_set():
                        raise RuntimeError(f"Worker {self.worker_id}: Population empty after catastrophe.")

                    stagnation_counter = 0
                    current_mutation_rate = self.config.hyper_mutation_rate
                elif stagnation_counter >= self.config.stagnation_limit:
                    if current_mutation_rate < self.config.hyper_mutation_rate - 0.01 and self.results_queue:
                         self.results_queue.put({"type": "status", "worker_id": self.worker_id, "message": f"W{self.worker_id} G{generation}: Stagnated. Hyper-mutate."})
                    current_mutation_rate = self.config.hyper_mutation_rate
                else:
                    current_mutation_rate = max(self.config.base_mutation_rate, current_mutation_rate * self.config.mutation_decay)
                
                # ... (Status reporting as before) ...
                if generation % 20 == 0 and self.results_queue:
                    time_factor_status = ""
                    if abs(self.config.time_score_factor - self.initial_config.time_score_factor) > 0.1 :
                        time_factor_status = f" DynTFact:{self.config.time_score_factor:.1f}"
                    self.results_queue.put({"type": "status", "worker_id": self.worker_id, "message": f"W{self.worker_id} G{generation}. BestFit:{best_fitness_local:.1f}. Mut:{current_mutation_rate:.2f}{time_factor_status}"})

                next_generation_chromos: List[List[Tuple[str,str]]] = []
                num_elites_next_gen = min(self.config.elitism_count, len(evaluated_population))
                next_generation_chromos.extend([c for _,_,c in evaluated_population[:num_elites_next_gen]])
                
                while len(next_generation_chromos) < self.config.population_size:
                    if self.stop_event.is_set(): break
                    actual_tourn_size = min(len(evaluated_population), self.config.tournament_size)
                    if actual_tourn_size == 0 : 
                         parents_selected_chromos = [self._generate_random_chromosome(), self._generate_random_chromosome()]
                    else:
                        p_data = [min(random.sample(evaluated_population, actual_tourn_size), key=lambda x:x[0]) for _ in range(2)]
                        parents_selected_chromos = [p[2] for p in p_data]

                    child1, child2 = self._crossover_chromosomes(parents_selected_chromos[0], parents_selected_chromos[1])
                    
                    if random.random() < current_mutation_rate:
                        child1 = self._mutate_chromosome(child1, current_mutation_rate) # Pass it here
                    if random.random() < current_mutation_rate:
                        child2 = self._mutate_chromosome(child2, current_mutation_rate) # And here
                    
                    next_generation_chromos.append(child1)
                    if len(next_generation_chromos) < self.config.population_size:
                        next_generation_chromos.append(child2)
                
                if self.stop_event.is_set(): break
                population = next_generation_chromos[:self.config.population_size]
                if not population and self.config.population_size > 0 and not self.stop_event.is_set():
                     raise RuntimeError(f"Worker {self.worker_id}: Population empty end of gen {generation}.")
                generation += 1
        # ... (exception handling and finally block)
        except Exception as e:
            import traceback 
            tb_str = traceback.format_exc()
            worker_id_val = getattr(self, 'worker_id', 'UNKNOWN_WORKER')
            error_message = f"Worker {worker_id_val} CRASHED in run(): {type(e).__name__}: {e}\nFull Traceback:\n{tb_str}"
            
            if hasattr(self, 'results_queue') and self.results_queue is not None:
                try:
                    self.results_queue.put({"type": "error", "worker_id": worker_id_val, "message": error_message})
                except Exception as q_err:
                    print(f"WORKER {worker_id_val} FAILED TO SEND ERROR TO QUEUE: {q_err}\n{error_message}", file=sys.stderr)
            else:
                print(f"WORKER {worker_id_val} ERROR (no results_queue): {error_message}", file=sys.stderr)
        finally:
            if 'error_message' not in locals() and hasattr(self, 'results_queue') and self.results_queue is not None:
                try:
                    final_status_msg = f"Worker {getattr(self, 'worker_id', 'UNKNOWN')} finished."
                    if hasattr(self, 'stop_event') and self.stop_event and self.stop_event.is_set():
                        final_status_msg = f"Worker {getattr(self, 'worker_id', 'UNKNOWN')} stopped by event."
                    
                    self.results_queue.put({"type": "status", "worker_id": getattr(self, 'worker_id', 'UNKNOWN'), "message": final_status_msg})
                except Exception:
                    pass

    def _simulate_chromosome(self, chromosome: List[Tuple[str, str]]) -> Optional[GameState]:
        current_state = GameState()

        for i, (action_type, item_code) in enumerate(chromosome):
            if current_state.time > 40000:
                return None
            next_simulated_state = GameLogic.get_simulated_action_outcome(
                current_state, action_type, item_code,
                self.config.metal_waste_to_bp_ratio,
                self.config.energy_waste_to_bp_ratio,
                self.config.energy_conversion_threshold_percentage, 
                self.config.energy_to_metal_conversion_rate       
            )

            if next_simulated_state is None:
                return None
            current_state = next_simulated_state

            while GameLogic.is_goal_step_complete(current_state, self.goal_sequence) and \
                  current_state.goal_step < len(self.goal_sequence):
                current_state = GameState(**{**vars(current_state), 'goal_step': current_state.goal_step + 1})

        if current_state.goal_step < len(self.goal_sequence):
            return None
        
        return current_state
      
    def run(self):
        try:
            population = []
            num_heuristic_to_generate = min(self.config.heuristic_seed_count, self.config.population_size)
            for _ in range(num_heuristic_to_generate):
                if self.stop_event.is_set(): break
                population.append(self._generate_random_chromosome(use_heuristic_start=True))
            
            if not self.stop_event.is_set():
                num_random_to_generate = max(0, self.config.population_size - len(population))
                for _ in range(num_random_to_generate):
                    if self.stop_event.is_set(): break
                    population.append(self._generate_random_chromosome())
            
            if not population and self.config.population_size > 0 and not self.stop_event.is_set():
                raise RuntimeError(f"Worker {self.worker_id}: Population is empty after init.")

            best_solution_local: Optional[GameState] = None
            best_fitness_local = float('inf')
            stagnation_counter = 0
            current_mutation_rate = self.config.base_mutation_rate
            generation = 0

            # Reset dynamic time factor tracker for this worker's run/reset
            self.time_improvement_tracker = {'last_best_time_for_factor_adj': float('inf'), 'generations_since_time_improvement': 0}


            while not self.stop_event.is_set():
                if self.pause_event.is_set():
                    initial_pause_sent = False # Renamed to avoid conflict
                    if self.results_queue and not initial_pause_sent:
                        try:
                            self.results_queue.put({"type": "status", "worker_id": self.worker_id, "message": f"W{self.worker_id} Paused"})
                            initial_pause_sent = True
                        except Exception: pass 

                    while self.pause_event.is_set() and not self.stop_event.is_set():
                        time.sleep(0.5)
                    
                    if self.stop_event.is_set(): break
                    if self.results_queue: 
                        try:
                            self.results_queue.put({"type": "status", "worker_id": self.worker_id, "message": f"W{self.worker_id} Resuming..."})
                        except Exception: pass

                evaluated_population: List[Tuple[float, GameState, List[Tuple[str,str]]]] = []
                for chromo_idx, chromo in enumerate(population):
                    if self.stop_event.is_set(): break
                    final_state = self._simulate_chromosome(chromo) # <<-- THIS CALL SHOULD NOW WORK
                    if final_state:
                        # Pass the worker's current (potentially dynamic) config
                        fitness = self.calculate_efficiency_score(final_state, self.config) 
                        evaluated_population.append((fitness, final_state, chromo))
                
                if self.stop_event.is_set(): break

                if not evaluated_population:
                    if self.config.population_size > 0 and not self.stop_event.is_set():
                        if self.results_queue:
                            try:
                                self.results_queue.put({"type": "status", "worker_id": self.worker_id, "message": f"W{self.worker_id} G{generation}: No valid solutions, re-pop."})
                            except Exception: pass
                        
                        population = []
                        num_h_regen = min(self.config.heuristic_seed_count, self.config.population_size)
                        for _ in range(num_h_regen):
                            if self.stop_event.is_set(): break
                            population.append(self._generate_random_chromosome(use_heuristic_start=True))
                        
                        if not self.stop_event.is_set():
                            num_r_regen = max(0, self.config.population_size - len(population))
                            for _ in range(num_r_regen):
                                if self.stop_event.is_set(): break
                                population.append(self._generate_random_chromosome())

                        if not population and not self.stop_event.is_set():
                             if self.results_queue: self.results_queue.put({"type": "status", "worker_id": self.worker_id, "message": f"W{self.worker_id} G{generation}: Re-pop failed."})
                             time.sleep(1)
                    stagnation_counter +=1
                    generation += 1
                    continue

                evaluated_population.sort(key=lambda x: x[0])
                current_best_fitness_in_gen, current_best_state_in_gen, _ = evaluated_population[0]
                
                # --- Conceptual Dynamic time_score_factor adjustment ---
                # This is a place you could put the logic from the previous suggestion
                if current_best_state_in_gen and current_best_state_in_gen.goal_step >= len(self.goal_sequence):
                    new_best_time_this_gen = current_best_state_in_gen.time
                    if new_best_time_this_gen < self.time_improvement_tracker['last_best_time_for_factor_adj']:
                        self.time_improvement_tracker['last_best_time_for_factor_adj'] = new_best_time_this_gen
                        self.time_improvement_tracker['generations_since_time_improvement'] = 0
                    else:
                        self.time_improvement_tracker['generations_since_time_improvement'] += 1

                    TARGET_TIME_IMPROVEMENT_WINDOW = self.initial_config.stagnation_limit // 2 
                    TIME_FACTOR_INCREMENT = self.initial_config.time_score_factor * 0.05 
                    MAX_TIME_FACTOR = self.initial_config.time_score_factor * 5 

                    if (self.time_improvement_tracker['generations_since_time_improvement'] >= TARGET_TIME_IMPROVEMENT_WINDOW and
                        stagnation_counter < self.initial_config.stagnation_limit // 2 and # Avoid if generally stagnated
                        self.config.time_score_factor < MAX_TIME_FACTOR):
                        
                        original_factor = self.config.time_score_factor
                        self.config.time_score_factor += TIME_FACTOR_INCREMENT
                        self.config.time_score_factor = min(self.config.time_score_factor, MAX_TIME_FACTOR)
                        self.time_improvement_tracker['generations_since_time_improvement'] = 0 
                        
                        if self.results_queue and abs(self.config.time_score_factor - original_factor) > 0.01:
                            self.results_queue.put({
                                "type": "status", "worker_id": self.worker_id,
                                "message": f"W{self.worker_id} G{generation}: Time stagn. Inc time_factor to {self.config.time_score_factor:.1f}"
                            })
                # --- End dynamic time_score_factor adjustment ---


                if current_best_fitness_in_gen < best_fitness_local:
                    best_fitness_local = current_best_fitness_in_gen
                    best_solution_local = current_best_state_in_gen
                    stagnation_counter = 0
                    current_mutation_rate = self.config.base_mutation_rate # Reset mutation on improvement
                    if self.results_queue:
                        self.results_queue.put({"type": "solution", "solution": best_solution_local, "generation": generation, "worker_id": self.worker_id, "fitness": best_fitness_local})
                else:
                    stagnation_counter += 1

                if stagnation_counter >= self.config.catastrophe_limit:
                    if self.results_queue: self.results_queue.put({"type": "status", "worker_id": self.worker_id, "message": f"W{self.worker_id} G{generation}: Catastrophe! Reset."})
                    
                    self.config = copy.deepcopy(self.initial_config) # Reset config to initial
                    self.time_improvement_tracker = {'last_best_time_for_factor_adj': float('inf'), 'generations_since_time_improvement': 0}


                    num_elites_cat = min(self.config.elitism_count, len(evaluated_population))
                    elite_chromos = [c for _,_,c in evaluated_population[:num_elites_cat]]
                    
                    seeds_to_add = []
                    num_seeds_cat = min(self.config.heuristic_seed_count * 2, self.config.population_size - len(elite_chromos))
                    if self.config.heuristic_seed_count > 0 and num_seeds_cat > 0:
                        for _ in range(num_seeds_cat):
                            if self.stop_event.is_set(): break
                            seeds_to_add.append(self._generate_random_chromosome(use_heuristic_start=True))
                    if self.stop_event.is_set(): break

                    randoms_needed = max(0, self.config.population_size - len(elite_chromos) - len(seeds_to_add))
                    randoms_to_add = []
                    for _ in range(randoms_needed):
                        if self.stop_event.is_set(): break
                        randoms_to_add.append(self._generate_random_chromosome())
                    if self.stop_event.is_set(): break

                    population = (elite_chromos + seeds_to_add + randoms_to_add)[:self.config.population_size]
                    if not population and self.config.population_size > 0 and not self.stop_event.is_set():
                        raise RuntimeError(f"Worker {self.worker_id}: Population empty after catastrophe.")
                    stagnation_counter = 0
                    current_mutation_rate = self.config.hyper_mutation_rate
                
                elif stagnation_counter >= self.config.stagnation_limit:
                    if current_mutation_rate < self.config.hyper_mutation_rate - 0.01 and self.results_queue: # Avoid spamming
                         self.results_queue.put({"type": "status", "worker_id": self.worker_id, "message": f"W{self.worker_id} G{generation}: Stagnated. Hyper-mutate."})
                    current_mutation_rate = self.config.hyper_mutation_rate
                else:
                    current_mutation_rate = max(self.config.base_mutation_rate, current_mutation_rate * self.config.mutation_decay)

                if generation % 20 == 0 and self.results_queue:
                    # Include current dynamic time_score_factor in status if it's different from initial
                    time_factor_status = ""
                    if abs(self.config.time_score_factor - self.initial_config.time_score_factor) > 0.1 :
                        time_factor_status = f" DynTFact:{self.config.time_score_factor:.1f}"

                    self.results_queue.put({"type": "status", "worker_id": self.worker_id, "message": f"W{self.worker_id} G{generation}. BestFit:{best_fitness_local:.1f}. Mut:{current_mutation_rate:.2f}{time_factor_status}"})

                next_generation_chromos: List[List[Tuple[str,str]]] = []
                num_elites_next_gen = min(self.config.elitism_count, len(evaluated_population))
                next_generation_chromos.extend([c for _,_,c in evaluated_population[:num_elites_next_gen]])
                
                if not evaluated_population:
                     population = [] 
                     generation +=1
                     continue

                while len(next_generation_chromos) < self.config.population_size:
                    if self.stop_event.is_set(): break
                    
                    actual_tourn_size = min(len(evaluated_population), self.config.tournament_size)
                    if actual_tourn_size == 0 : 
                         parents_selected_chromos = [self._generate_random_chromosome(), self._generate_random_chromosome()]
                    else:
                        p_data = [min(random.sample(evaluated_population, actual_tourn_size), key=lambda x:x[0]) for _ in range(2)]
                        parents_selected_chromos = [p[2] for p in p_data]

                    child1, child2 = self._crossover_chromosomes(parents_selected_chromos[0], parents_selected_chromos[1])
                                    
                    if random.random() < current_mutation_rate: # This is the probability of applying mutation
                        child1 = self._mutate_chromosome(child1, current_mutation_rate) 
                    if random.random() < current_mutation_rate: # This is the probability of applying mutation
                        child2 = self._mutate_chromosome(child2, current_mutation_rate)
                    
                    next_generation_chromos.append(child1)
                    if len(next_generation_chromos) < self.config.population_size:
                        next_generation_chromos.append(child2)
                
                if self.stop_event.is_set(): break
                population = next_generation_chromos[:self.config.population_size]
                if not population and self.config.population_size > 0 and not self.stop_event.is_set():
                     raise RuntimeError(f"Worker {self.worker_id}: Population empty end of gen {generation}.")
                generation += 1

        except Exception as e:
            import traceback 
            tb_str = traceback.format_exc()
            worker_id_val = getattr(self, 'worker_id', 'UNKNOWN_WORKER')
            error_message = f"Worker {worker_id_val} CRASHED in run(): {type(e).__name__}: {e}\nFull Traceback:\n{tb_str}"
            
            if hasattr(self, 'results_queue') and self.results_queue is not None:
                try:
                    self.results_queue.put({"type": "error", "worker_id": worker_id_val, "message": error_message})
                except Exception as q_err:
                    print(f"WORKER {worker_id_val} FAILED TO SEND ERROR TO QUEUE: {q_err}\n{error_message}", file=sys.stderr)
            else:
                print(f"WORKER {worker_id_val} ERROR (no results_queue): {error_message}", file=sys.stderr)
        finally:
            if 'error_message' not in locals() and hasattr(self, 'results_queue') and self.results_queue is not None:
                try:
                    final_status_msg = f"Worker {getattr(self, 'worker_id', 'UNKNOWN')} finished."
                    if hasattr(self, 'stop_event') and self.stop_event and self.stop_event.is_set():
                        final_status_msg = f"Worker {getattr(self, 'worker_id', 'UNKNOWN')} stopped by event."
                    
                    self.results_queue.put({"type": "status", "worker_id": getattr(self, 'worker_id', 'UNKNOWN'), "message": final_status_msg})
                except Exception:
                    pass

def import_pygame_quietly():
    try:
        import pygame
        return pygame
    except ImportError:
        return None

class PygameVisualizer:
    """Visualizes a GameState solution using Pygame."""
    def __init__(self, solution_to_show: GameState, 
                 metal_waste_bp_ratio: float, 
                 energy_waste_bp_ratio: float,
                 energy_conversion_threshold_percentage: float,
                 energy_to_metal_conversion_rate: float):
        self.solution_to_show = solution_to_show
        # Store simulation parameters needed for re-simulating the path for keyframes
        self.metal_waste_bp_ratio = metal_waste_bp_ratio
        self.energy_waste_bp_ratio = energy_waste_bp_ratio
        self.energy_conversion_threshold_percentage = energy_conversion_threshold_percentage
        self.energy_to_metal_conversion_rate = energy_to_metal_conversion_rate

    @staticmethod
    def _parse_viz_action_string(action_str: str) -> Tuple[str, str, str]:
        """Parses an action string from GameState.path for display."""
        parts = action_str.split() # e.g. "Build ME", "Upgrade BL to ABL"
        action_type_display = parts[0] # "Build", "Upgrade", "Reclaim"
        
        item_code_display = "N/A"
        full_display_name = action_str # Default to full string

        if action_type_display.lower() == ACTION_UPGRADE and len(parts) >= 4 and parts[2].lower() == "to":
            # "Upgrade BL to ABL"
            base_code = parts[1]
            target_code = parts[3]
            base_name = UNITS_DATA.get(base_code, {}).get('Name', base_code)
            target_name = UNITS_DATA.get(target_code, {}).get('Name', target_code)
            full_display_name = f"Upgrade {base_name} to {target_name}"
            item_code_display = base_code # The item being acted upon
        elif len(parts) >= 2:
            # "Build ME", "Reclaim BL"
            item_code_display = parts[1]
            item_name = UNITS_DATA.get(item_code_display, {}).get('Name', item_code_display)
            full_display_name = f"{action_type_display} {item_name}"
        
        # Determine the internal action_type (build, upgrade, reclaim)
        internal_action_type = action_type_display.lower()

        return internal_action_type, item_code_display, full_display_name


    def run(self):
        """Runs the Pygame visualization loop."""
        # No 'self.' needed here, it's a global function from the module
        pg_module = import_pygame_quietly()
        if not pg_module:
            print("Pygame could not be imported. Visualization unavailable.")
            # Fallback to console print of the path
            print("\n--- Best Solution Path ---")
            if self.solution_to_show and self.solution_to_show.path:
                for i, step_str in enumerate(self.solution_to_show.path):
                    print(f"{i+1}. {step_str}")
                mins, secs = divmod(self.solution_to_show.time, 60)
                print(f"Total Time: {int(mins):02d}:{int(secs):02d}")
            else:
                print("No solution to display.")
            return

        pg = pg_module 

        initial_state = GameState() # A base state to start interpolation from
        pg.init()
        WIDTH, HEIGHT, FONT_SIZE = 1400, 850, 18
        REPLAY_SPEED_DEFAULT = 15.0
        replay_speed = REPLAY_SPEED_DEFAULT

        COLORS = {'bg': (10, 20, 30), 'text':(220, 220, 220), 'metal':(150, 150, 200), 
                  'energy':(220, 220, 100), 'bar_bg':(40, 50, 60), 'header':(180, 180, 255),
                  'action_progress':(100, 200, 100), 'reclaim_progress':(220,100,100), 
                  'waste':(200, 100, 100), 'pos_eco':(120,220,120), 'neg_eco': (220,120,120),
                  'executor': (160, 160, 160), 'timeline_bg': (30,40,50), 'timeline_fg': (100,120,140),
                  'timeline_marker': (255,0,0), 'action_log_bg': (20,30,40), 'current_action_highlight': (50,60,80)}

        screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("RTS Build Order Visualizer")
        clock = pg.time.Clock()
        try: # Try specific font, fallback
            font = pg.font.SysFont("Consolas", FONT_SIZE) 
            header_font = pg.font.SysFont("Consolas", FONT_SIZE + 4, bold=True)
        except:
            font = pg.font.Font(None, FONT_SIZE + 2) 
            header_font = pg.font.Font(None, FONT_SIZE + 6)
        
        # Prepare keyframes from the solution path
        keyframes = [initial_state]
        temp_state_for_keyframes = initial_state
        if self.solution_to_show and self.solution_to_show.path:
            for action_str_in_path in self.solution_to_show.path:
                action_type_internal, item_code_internal, _ = self._parse_viz_action_string(action_str_in_path)
                
                # Use the stored simulation parameters
                next_s_kf = GameLogic.get_simulated_action_outcome(
                    temp_state_for_keyframes,
                    action_type_internal, 
                    item_code_internal,
                    self.metal_waste_bp_ratio,              # Pass stored value
                    self.energy_waste_bp_ratio,             # Pass stored value
                    self.energy_conversion_threshold_percentage, # Pass stored value
                    self.energy_to_metal_conversion_rate      # Pass stored value
                ) 
                if next_s_kf is None: 
                    # Attempt to provide more context if a specific action fails resimulation
                    error_msg_viz = f"Error: Viz failed to re-simulate action: {action_str_in_path} from state {temp_state_for_keyframes.time:.1f}s. This might indicate an issue with the action's validity or simulation logic under visualizer params."
                    print(error_msg_viz, file=sys.stderr)
                    # Optionally, you could try to skip this keyframe or stop visualization
                    # For now, we'll break, which will likely lead to "Not enough keyframes"
                    break 
                temp_state_for_keyframes = next_s_kf
                keyframes.append(temp_state_for_keyframes)
        
        if len(keyframes) <= 1:
            print("Not enough keyframes to visualize.")
            pg.quit()
            return

        running, paused = True, False
        game_time_visual = 0.0 
        keyframe_idx = 0 

        timeline_rect = pg.Rect(50, HEIGHT - 80, WIDTH - 100, 20)
        action_log_rect = pg.Rect(WIDTH - 450, 250, 430, HEIGHT - 250 - 100) 
        action_log_scroll_offset = 0
        max_log_lines_visible = (action_log_rect.height - 35) // (FONT_SIZE + 2)


        while running:
            dt = clock.tick(60) / 1000.0 

            for event in pg.event.get():
                if event.type == pg.QUIT: running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE: paused = not paused
                    if event.key == pg.K_EQUALS or event.key == pg.K_PLUS: 
                        replay_speed = min(100.0, replay_speed * 1.5)
                    if event.key == pg.K_MINUS: 
                        replay_speed = max(0.1, replay_speed / 1.5) # Allow slower speed
                    if event.key == pg.K_LEFT: 
                        keyframe_idx = max(0, keyframe_idx -1)
                        game_time_visual = keyframes[keyframe_idx].time
                    if event.key == pg.K_RIGHT: 
                         if keyframe_idx < len(keyframes) - 2:
                            keyframe_idx +=1
                            game_time_visual = keyframes[keyframe_idx].time
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1 and timeline_rect.collidepoint(event.pos): 
                        progress_clicked = (event.pos[0] - timeline_rect.x) / timeline_rect.width
                        target_time = progress_clicked * keyframes[-1].time
                        for i, kf in enumerate(keyframes):
                            if kf.time >= target_time:
                                keyframe_idx = max(0, i-1) 
                                game_time_visual = target_time
                                break
                    if action_log_rect.collidepoint(event.pos) and self.solution_to_show.path:
                        total_log_height = len(self.solution_to_show.path) * (FONT_SIZE + 2)
                        if event.button == 4:  # Scroll up
                            action_log_scroll_offset = max(0, action_log_scroll_offset - (FONT_SIZE + 2) * 3) # Scroll 3 lines
                        elif event.button == 5:  # Scroll down
                            max_scroll = max(0, total_log_height - action_log_rect.height + 35) # +35 for header
                            action_log_scroll_offset = min(max_scroll, action_log_scroll_offset + (FONT_SIZE + 2) * 3)


            if not running: break
            
            if not paused:
                game_time_visual += dt * replay_speed
            
            while keyframe_idx < len(keyframes) - 1 and game_time_visual >= keyframes[keyframe_idx+1].time:
                keyframe_idx += 1
            
            if game_time_visual >= keyframes[-1].time:
                game_time_visual = keyframes[-1].time
                keyframe_idx = len(keyframes) - 2 
                paused = True 

            prev_frame = keyframes[keyframe_idx]
            next_frame = keyframes[keyframe_idx+1] if keyframe_idx + 1 < len(keyframes) else prev_frame
            
            action_duration = next_frame.time - prev_frame.time
            time_into_action = game_time_visual - prev_frame.time
            progress_ratio = time_into_action / action_duration if action_duration > 1e-9 else 1.0
            progress_ratio = max(0, min(1, progress_ratio)) 

            interp_metal = prev_frame.metal + (next_frame.metal - prev_frame.metal) * progress_ratio
            interp_energy = prev_frame.energy + (next_frame.energy - prev_frame.energy) * progress_ratio
            interp_waste_m = prev_frame.wasted_metal + (next_frame.wasted_metal - prev_frame.wasted_metal) * progress_ratio
            interp_waste_e = prev_frame.wasted_energy + (next_frame.wasted_energy - prev_frame.wasted_energy) * progress_ratio
            interp_bp = next_frame.buildpower if progress_ratio > 0.95 else prev_frame.buildpower

            display_state_vars = vars(next_frame).copy() 
            display_state_vars.update({
                'time': game_time_visual, 'metal': max(0, interp_metal), 'energy': max(0, interp_energy),
                'wasted_metal': interp_waste_m, 'wasted_energy': interp_waste_e,
                'buildpower': interp_bp,
                'metal_income': next_frame.metal_income, 'energy_income': next_frame.energy_income,
                'max_metal': next_frame.max_metal, 'max_energy': next_frame.max_energy,
                'units': next_frame.units 
            })
            current_display_state = GameState(**display_state_vars)
            
            current_action_str_from_path = "Starting..."
            current_action_type_viz = "" 
            current_item_code_viz = ""
            if self.solution_to_show.path and keyframe_idx < len(self.solution_to_show.path):
                current_action_type_viz, current_item_code_viz, current_action_str_from_path = \
                    self._parse_viz_action_string(self.solution_to_show.path[keyframe_idx])

            screen.fill(COLORS['bg'])
            
            y_pos = 20
            screen.blit(header_font.render("METAL", True, COLORS['metal']), (50, y_pos))
            m_bar_rect = pg.Rect(50, y_pos + 40, 500, 30)
            pg.draw.rect(screen, COLORS['bar_bg'], m_bar_rect)
            m_fill_ratio = current_display_state.metal / current_display_state.max_metal if current_display_state.max_metal > 0 else 0
            pg.draw.rect(screen, COLORS['metal'], (m_bar_rect.x, m_bar_rect.y, m_fill_ratio * m_bar_rect.width, m_bar_rect.height))
            m_text_surf = font.render(f"{int(current_display_state.metal)} / {current_display_state.max_metal}", True, COLORS['text'])
            screen.blit(m_text_surf, m_text_surf.get_rect(center=m_bar_rect.center))
            m_income_color = COLORS['pos_eco'] if current_display_state.metal_income >= 0 else COLORS['neg_eco']
            screen.blit(font.render(f"{current_display_state.metal_income:+.1f}/s", True, m_income_color), (m_bar_rect.right + 10, m_bar_rect.centery - FONT_SIZE//2))

            screen.blit(header_font.render("ENERGY", True, COLORS['energy']), (WIDTH // 2, y_pos))
            e_bar_rect = pg.Rect(WIDTH // 2, y_pos + 40, 500, 30)
            pg.draw.rect(screen, COLORS['bar_bg'], e_bar_rect)
            e_fill_ratio = current_display_state.energy / current_display_state.max_energy if current_display_state.max_energy > 0 else 0
            pg.draw.rect(screen, COLORS['energy'], (e_bar_rect.x, e_bar_rect.y, e_fill_ratio * e_bar_rect.width, e_bar_rect.height))
            e_text_surf = font.render(f"{int(current_display_state.energy)} / {current_display_state.max_energy}", True, COLORS['text'])
            screen.blit(e_text_surf, e_text_surf.get_rect(center=e_bar_rect.center))
            e_income_color = COLORS['pos_eco'] if current_display_state.energy_income >= 0 else COLORS['neg_eco']
            screen.blit(font.render(f"{current_display_state.energy_income:+.1f}/s", True, e_income_color), (e_bar_rect.right + 10, e_bar_rect.centery - FONT_SIZE//2))
            
            y_pos += 90
            time_mins, time_secs = divmod(int(game_time_visual), 60)
            screen.blit(header_font.render(f"TIME: {time_mins:02d}:{time_secs:02d}", True, COLORS['text']), (50, y_pos))
            screen.blit(header_font.render(f"BUILDPOWER: {current_display_state.buildpower}", True, COLORS['text']), (WIDTH // 2, y_pos))
            
            y_pos += 40
            screen.blit(font.render(f"Total M Cost: {int(self.solution_to_show.total_metal_cost)}", True, COLORS['metal']), (50, y_pos))
            screen.blit(font.render(f"Replay Speed: {replay_speed:.1f}x {'(PAUSED)' if paused else ''}", True, COLORS['text']), (WIDTH // 2, y_pos)) # Show pause status
            
            y_pos += 30
            screen.blit(font.render(f"Wasted M: {int(current_display_state.wasted_metal)}", True, COLORS['waste']), (50, y_pos))
            screen.blit(font.render(f"Wasted E: {int(current_display_state.wasted_energy)}", True, COLORS['waste']), (WIDTH // 2, y_pos))

            action_y_start = y_pos + 50
            screen.blit(header_font.render("CURRENT ACTION", True, COLORS['header']), (50, action_y_start))
            
            action_details_y = action_y_start + 40
            screen.blit(font.render(current_action_str_from_path, True, COLORS['text']), (50, action_details_y)); action_details_y += 25
            
            target_unit_for_action_viz = GameLogic.get_item_to_build(current_action_type_viz, current_item_code_viz)
            if target_unit_for_action_viz and current_action_type_viz != ACTION_RECLAIM: 
                unit_info_viz = UNITS_DATA[target_unit_for_action_viz]
                m_c, e_c, bt = unit_info_viz.get(RESOURCE_METAL,0), unit_info_viz.get(RESOURCE_ENERGY,0), unit_info_viz.get('Buildtime',0)
                
                executor_bp_viz = 100 if target_unit_for_action_viz in FACTORY_UNITS else prev_frame.buildpower 
                m_drain_viz = (m_c / bt * executor_bp_viz / 100) if bt > 0 and executor_bp_viz > 0 else 0
                e_drain_viz = (e_c / bt * executor_bp_viz / 100) if bt > 0 and executor_bp_viz > 0 else 0
                
                screen.blit(font.render(f"Cost: {int(m_c)} M, {int(e_c)} E", True, COLORS['text']), (50, action_details_y)); action_details_y += 25
                screen.blit(font.render(f"Drain: {m_drain_viz:.1f}M/s, {e_drain_viz:.1f}E/s (at {executor_bp_viz} BP)", True, COLORS['text']), (50, action_details_y)); action_details_y += 25

            progress_bar_rect = pg.Rect(50, action_details_y, 500, 20)
            pg.draw.rect(screen, COLORS['bar_bg'], progress_bar_rect)
            p_bar_color = COLORS['reclaim_progress'] if current_action_type_viz == ACTION_RECLAIM else COLORS['action_progress']
            pg.draw.rect(screen, p_bar_color, (progress_bar_rect.x, progress_bar_rect.y, progress_ratio * progress_bar_rect.width, progress_bar_rect.height))

            unit_list_x = WIDTH // 2 + 100 # Shifted right for action log
            unit_list_y_start = y_pos + 50 
            screen.blit(header_font.render("UNITS & ECONOMY", True, COLORS['header']), (unit_list_x, unit_list_y_start))
            
            unit_display_y = unit_list_y_start + 40
            max_unit_list_height = timeline_rect.y - unit_display_y - 20 
            
            screen.blit(font.render("--- Buildings ---", True, COLORS['header']), (unit_list_x + 20, unit_display_y)); unit_display_y += FONT_SIZE + 4
            for unit, count in sorted(current_display_state.get_unit_counts().items()):
                if count > 0 and unit not in FACTORY_UNITS and unit_display_y < max_unit_list_height : 
                    info = UNITS_DATA.get(unit, {}); eco_parts = []
                    
                    net_m = (info.get('Output',{}).get(RESOURCE_METAL,0) - info.get('Input',{}).get(RESOURCE_METAL,0)) * count
                    net_e = (info.get('Output',{}).get(RESOURCE_ENERGY,0) - info.get('Input',{}).get(RESOURCE_ENERGY,0)) * count
                    if net_m != 0: eco_parts.append(f"{net_m:+.1f}M")
                    if net_e != 0: eco_parts.append(f"{net_e:+.1f}E")

                    eco_str = f"({', '.join(eco_parts)})" if eco_parts else ""
                    screen.blit(font.render(f"{count}x {info.get('Name', unit)} {eco_str}", True, COLORS['text']), (unit_list_x + 40, unit_display_y)); unit_display_y += FONT_SIZE + 2
            
            unit_display_y += 10 
            if unit_display_y < max_unit_list_height:
                screen.blit(font.render("--- Mobile Units ---", True, COLORS['header']), (unit_list_x + 20, unit_display_y)); unit_display_y += FONT_SIZE + 4
            for unit, count in sorted(current_display_state.get_unit_counts().items()):
                if count > 0 and unit in FACTORY_UNITS and unit_display_y < max_unit_list_height: 
                    info = UNITS_DATA.get(unit, {}); bp_out = info.get('Output',{}).get(RESOURCE_BUILDPOWER,0) * count
                    bp_str = f"(+{bp_out} BP)" if bp_out > 0 else ""
                    screen.blit(font.render(f"{count}x {info.get('Name', unit)} {bp_str}", True, COLORS['text']), (unit_list_x + 40, unit_display_y)); unit_display_y += FONT_SIZE + 2

            pg.draw.rect(screen, COLORS['timeline_bg'], timeline_rect)
            current_time_marker_x = timeline_rect.x + (game_time_visual / keyframes[-1].time) * timeline_rect.width
            pg.draw.line(screen, COLORS['timeline_marker'], (current_time_marker_x, timeline_rect.top), (current_time_marker_x, timeline_rect.bottom), 2)
            for kf_marker in keyframes:
                kf_marker_x = timeline_rect.x + (kf_marker.time / keyframes[-1].time) * timeline_rect.width
                pg.draw.line(screen, COLORS['timeline_fg'], (kf_marker_x, timeline_rect.top + 5), (kf_marker_x, timeline_rect.bottom - 5), 1)

            pg.draw.rect(screen, COLORS['action_log_bg'], action_log_rect) 
            pg.draw.rect(screen, COLORS['header'], action_log_rect, 1) 
            screen.blit(header_font.render("Build Order Path", True, COLORS['header']), (action_log_rect.x + 5, action_log_rect.y + 5))
            log_y_offset = action_log_rect.y + 35 - action_log_scroll_offset
            if self.solution_to_show.path:
                for i, action_log_entry_str in enumerate(self.solution_to_show.path):
                    if log_y_offset + FONT_SIZE > action_log_rect.y + 30 and log_y_offset < action_log_rect.bottom - 5 : 
                        is_current_action_in_log = (i == keyframe_idx)
                        log_color = COLORS['energy'] if is_current_action_in_log else COLORS['text']
                        
                        if is_current_action_in_log:
                            highlight_rect = pg.Rect(action_log_rect.x + 2, log_y_offset-1, action_log_rect.width - 4, FONT_SIZE + 2)
                            pg.draw.rect(screen, COLORS['current_action_highlight'], highlight_rect)

                        _, _, parsed_display_name = self._parse_viz_action_string(action_log_entry_str)
                        log_text_surf = font.render(f"{i+1}. {parsed_display_name}", True, log_color)
                        screen.blit(log_text_surf, (action_log_rect.x + 10, log_y_offset))
                    log_y_offset += FONT_SIZE + 2


            pg.display.flip()
            
        pg.quit()

class CursesApp:
    CACHE_DIR = "ga_solutions_cache"
    CONFIG_FILE = os.path.join(CACHE_DIR, "ga_config.json")

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.workers: List[Process] = []
        self.results_queue: Optional[Queue] = None
        self.stop_event: Optional[Event] = None
        self.pause_event: Optional[Event] = None
        
        self.goal_sequence: List[Tuple[str, str, int]] = [('build', 'AFR', 1)] 
        self.best_solution_so_far: Optional[GameState] = None
        self.best_fitness_so_far: float = float('inf')
        self.current_generation: int = 0
        # Ensure os.cpu_count() is imported if you use it here: import os
        self.num_workers = max(1, (os.cpu_count() or 1) -1) 
        self.worker_statuses: Dict[int, str] = {i: "Idle" for i in range(self.num_workers)}
        
        self.user_input: str = ""
        self.status_message: str = "Enter command (h for help). Default goal: 1 AFR"
        self.is_paused: bool = False
        self.ga_config = GeneticAlgorithmConfig() # Assumes GeneticAlgorithmConfig is defined
        self._load_ga_config()

        self.windows_need_recreate: bool = True
        self.status_win = None # Type: Optional[curses.window]
        self.worker_status_win = None # Type: Optional[curses.window]
        self.input_win = None # Type: Optional[curses.window]

        if not os.path.exists(self.CACHE_DIR):
            os.makedirs(self.CACHE_DIR)

    def _init_curses_windows(self):
        self.stdscr.erase() 
        height, width = self.stdscr.getmaxyx()
        
        min_height, min_width = 24, 80 
        if height < min_height or width < min_width:
            try: # Defensively try to addstr
                self.stdscr.addstr(0,0, f"Terminal too small. Min {min_width}x{min_height} required. Current: {width}x{height}")
                self.stdscr.refresh()
            except: pass # Curses might be unusable
            self.status_win, self.worker_status_win, self.input_win = None, None, None
            return False

        status_win_height = 10
        input_win_height = 3
        worker_win_height = height - status_win_height - input_win_height

        try:
            self.status_win = curses.newwin(status_win_height, width, 0, 0)
            self.worker_status_win = curses.newwin(worker_win_height, width, status_win_height, 0)
            self.input_win = curses.newwin(input_win_height, width, height - input_win_height, 0)
            self.windows_need_recreate = False
            return True
        except curses.error:
            try:
                self.stdscr.addstr(0,0, "Error creating Curses windows. Try resizing terminal.")
                self.stdscr.refresh()
            except: pass
            self.status_win, self.worker_status_win, self.input_win = None, None, None
            return False

    def _init_curses_settings(self):
        curses.curs_set(0) 
        self.stdscr.nodelay(True) 
        curses.start_color()
        # It's good practice to check if colors are supported
        if curses.has_colors():
            curses.use_default_colors() 
            bg_color = -1 # Use default terminal background
            # Fallback if default colors are not well supported by terminal with use_default_colors()
            # You might need to explicitly set bg_color = curses.COLOR_BLACK for some terminals
        else:
            bg_color = curses.COLOR_BLACK # No color support, use black


        # Initialize pairs, checking has_colors()
        if curses.has_colors():
            curses.init_pair(1, curses.COLOR_CYAN, bg_color)    
            curses.init_pair(2, curses.COLOR_GREEN, bg_color)   
            curses.init_pair(3, curses.COLOR_YELLOW, bg_color)  
            curses.init_pair(4, curses.COLOR_WHITE, bg_color)   
            curses.init_pair(5, curses.COLOR_MAGENTA, bg_color) 
            curses.init_pair(6, curses.COLOR_RED, bg_color)     
            curses.init_pair(7, curses.COLOR_BLUE, bg_color)    
        # If no colors, attributes like A_BOLD can still be used.

    def _get_solution_filepath(self, name: str) -> str:
        return os.path.join(self.CACHE_DIR, f"solution_{name.replace(' ','_')}.pkl")

    def _load_named_solution(self, name: str):
        filepath = self._get_solution_filepath(name)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'rb') as f:
                    data = pickle.load(f)
                    if isinstance(data, GameState):
                        self.best_solution_so_far = data
                        # Temporarily create a dummy runner instance for score calculation
                        # Ensure GeneticAlgorithmRunner can be instantiated with dummy queue/events if needed
                        temp_runner_config = self.ga_config # Or a fresh default if more appropriate
                        # Create minimal Queue and Event for this specific call, not affecting main ones
                        from multiprocessing import Queue as TempQueue, Event as TempEvent
                        dummy_queue = TempQueue()
                        dummy_event = TempEvent()

                        # Ensure GeneticAlgorithmRunner is defined or self.ga_config exists for this call
                        self.best_fitness_so_far = GeneticAlgorithmRunner(temp_runner_config, self.goal_sequence, dummy_queue, dummy_event, dummy_event, -1).calculate_efficiency_score(data)

                        self.status_message = f"Loaded solution '{name}' (old format)."
                    elif isinstance(data, dict) and "solution" in data and "fitness" in data:
                        self.best_solution_so_far = data["solution"]
                        self.best_fitness_so_far = data["fitness"]
                        self.status_message = f"Loaded solution '{name}' (Fitness: {self.best_fitness_so_far:.2f})."
                    else:
                        self.status_message = f"Error: Unknown format in solution file '{name}'."
            except Exception as e:
                # import traceback # Already imported at module level or can be here
                # tb_str = traceback.format_exc()
                self.status_message = f"Error loading solution '{name}': {type(e).__name__} - {e}"
                # Optionally log tb_str to a file if detailed debugging is needed here
        else:
            self.status_message = f"Solution '{name}' not found."

    def _save_current_solution(self, name: str):
        if self.best_solution_so_far:
            filepath = self._get_solution_filepath(name)
            try:
                data_to_save = {
                    "solution": self.best_solution_so_far,
                    "fitness": self.best_fitness_so_far,
                    "goal_sequence": self.goal_sequence, 
                    "ga_config_snapshot": self.ga_config.to_dict() 
                }
                with open(filepath, "wb") as f:
                    pickle.dump(data_to_save, f)
                self.status_message = f"Solution saved as '{name}'."
            except Exception as e:
                self.status_message = f"Error saving solution '{name}': {e}"
        else:
            self.status_message = "No best solution to save."

    def _list_saved_solutions(self) -> List[str]:
        solutions = []
        if not os.path.exists(self.CACHE_DIR): return []
        for f_name in os.listdir(self.CACHE_DIR):
            if f_name.startswith("solution_") and f_name.endswith(".pkl"):
                solutions.append(f_name[len("solution_"):-len(".pkl")].replace('_',' '))
        return solutions

    def _delete_saved_solution(self, name: str):
        filepath = self._get_solution_filepath(name)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                self.status_message = f"Solution '{name}' deleted."
            except Exception as e:
                self.status_message = f"Error deleting '{name}': {e}"
        else:
            self.status_message = f"Solution '{name}' not found for deletion."
            
    def _load_ga_config(self):
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    config_dict = json.load(f) # config_dict should have primitive values
                
                # --- THIS IS THE POINT OF INTEREST ---
                # Ensure config_dict read from JSON contains actual values,
                # not string representations of Field objects or anything strange.
                # For example, config_dict["energy_to_metal_conversion_rate"] should be 0.01 (a float)
                # and not the string "Field(default=0.01, ...)"

                # The from_dict method itself looks okay if 'config_dict' is clean.
                self.ga_config = GeneticAlgorithmConfig.from_dict(config_dict)
                # self.status_message = "Loaded GA config from file."
            except Exception as e:
                self.status_message = f"Error loading GA config, using defaults: {e}"
                self.ga_config = GeneticAlgorithmConfig() # Fallback to default INSTANCE
        else:
             self.ga_config = GeneticAlgorithmConfig() # Default INSTANCE if no file

    def _save_ga_config(self):
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self.ga_config.to_dict(), f, indent=4)
            self.status_message = "GA config saved."
        except Exception as e:
            self.status_message = f"Error saving GA config: {e}"

    def _stop_all_workers(self): # As before
        if not self.workers: return
        self.status_message = "Stopping workers..."
        if self.status_win: self._draw_ui(); curses.doupdate()

        if self.stop_event: self.stop_event.set()
        if self.pause_event and self.pause_event.is_set(): self.pause_event.clear() 
        
        for i, worker in enumerate(self.workers):
            self.worker_statuses[i] = "Terminating..."
            if self.status_win: self._draw_ui(); curses.doupdate()
            worker.join(timeout=1.5) # Slightly shorter timeout
            if worker.is_alive():
                worker.terminate() 
                worker.join(timeout=0.5)
        self.workers.clear()
        self.worker_statuses = {i: "Idle" for i in range(self.num_workers)}
        self.status_message = "Workers stopped."

    def _start_new_worker_pool(self): # As before
        self._stop_all_workers() 
        self.current_generation = 0
        self.worker_statuses = {i: "Initializing..." for i in range(self.num_workers)}
        
        self.results_queue = Queue()
        self.stop_event = Event()
        self.pause_event = Event() 

        for i in range(self.num_workers):
            runner = GeneticAlgorithmRunner(
                self.ga_config,  # Pass the instance directly
                list(self.goal_sequence),
                self.results_queue, self.stop_event, self.pause_event, i
            )
            process = Process(target=runner.run, daemon=True) 
            process.start()
            self.workers.append(process)
        
        self.status_message = f"Started {self.num_workers} workers."
        if self.is_paused and self.pause_event: 
            self.pause_event.set()
            self.worker_statuses = {i: "Paused (Initial)" for i in range(self.num_workers)}

    @staticmethod
    def parse_goal_string(goal_str: str) -> Optional[List[Tuple[str, str, int]]]: # As before
        sequence: List[Tuple[str, str, int]] = []
        steps = goal_str.lower().split(' then ')
        for step_idx, step_str in enumerate(steps):
            parts = step_str.strip().split()
            if not parts: continue
            action = ACTION_BUILD 
            if parts[0] == ACTION_RECLAIM:
                action = ACTION_RECLAIM; parts.pop(0)
            elif parts[0] == ACTION_UPGRADE: 
                action = ACTION_UPGRADE; parts.pop(0)
                count = 1; item_to_upgrade = ""
                if parts[0].isdigit() : 
                    count = int(parts[0])
                    item_to_upgrade = "".join(parts[1:parts.index("to")]) if "to" in parts else ""
                else: 
                    item_to_upgrade = "".join(parts[0:parts.index("to")]) if "to" in parts else ""
                if not item_to_upgrade or "to" not in parts : return None 
                code = NAME_TO_CODE.get(item_to_upgrade.lower().replace(' ', ''))
                if not code or code not in UPGRADE_MAP: return None 
                sequence.append((action, code, count))
                continue
            try:
                count_str = parts[0]
                if count_str.endswith('x'): count_str = count_str[:-1]
                if count_str.isdigit(): count = int(count_str); name_parts = parts[1:]
                else: count = 1; name_parts = parts
                name = "".join(name_parts).lower()
                code = NAME_TO_CODE.get(name)
                if code:
                    if action == ACTION_RECLAIM and count == 1 and step_idx == len(steps) -1:
                         sequence.append((action, code, 0)) 
                    else: sequence.append((action, code, count))
                else: return None 
            except (ValueError, IndexError): return None 
        return sequence if sequence else None

    def _handle_input(self, key_code: int): # As before
        if key_code == curses.KEY_RESIZE:
            self.windows_need_recreate = True
            return True

        if key_code == curses.KEY_ENTER or key_code in [10, 13]:
            command_full = self.user_input.strip()
            self.user_input = "" 
            if not command_full: return True
            command_parts = command_full.lower().split()
            command = command_parts[0]; args = command_parts[1:]

            if command in ['h', 'help']: self.status_message = "Cmds: g(oal), v(is), p(ause)/r(esume), run, stop, q(uit), save, load, ls, del, conf"
            elif command in ['q', 'quit', 'exit']: return False
            elif command in ['v', 'visualize', 'vis']:
                if self.best_solution_so_far:
                    self.status_message = "Starting visualizer..."
                    if self.status_win: self._draw_ui(); curses.doupdate()
                    
                    # Create PygameVisualizer instance with necessary config values
                    visualizer_instance = PygameVisualizer(
                        self.best_solution_so_far,
                        self.ga_config.metal_waste_to_bp_ratio,
                        self.ga_config.energy_waste_to_bp_ratio,
                        self.ga_config.energy_conversion_threshold_percentage,
                        self.ga_config.energy_to_metal_conversion_rate
                    )
                    vis_process = Process(target=visualizer_instance.run, daemon=True)
                    vis_process.start()
                else:
                    self.status_message = "No solution to visualize."
            elif command in ['p', 'pause']:
                self.is_paused = True
                if self.pause_event: self.pause_event.set()
                self.status_message = "Execution paused."; self.worker_statuses = {i: "Paused" for i in self.worker_statuses}
            elif command in ['r', 'resume', 'run', 's', 'start']:
                self.is_paused = False
                if not self.workers or all(not w.is_alive() for w in self.workers): 
                    self.status_message = "Starting new GA run..."; self._start_new_worker_pool()
                elif self.pause_event: 
                     self.pause_event.clear(); self.status_message = "Execution resumed."
                     self.worker_statuses = {i: "Resuming..." for i in self.worker_statuses}
                else: self.status_message = "No active workers, starting new..."; self._start_new_worker_pool()
            elif command == 'stop': self._stop_all_workers(); self.status_message = "GA run stopped."
            elif command in ['g', 'goal']:
                goal_str = " ".join(args)
                new_goal_seq = self.parse_goal_string(goal_str)
                if new_goal_seq:
                    self.goal_sequence = new_goal_seq; self.best_solution_so_far = None; self.best_fitness_so_far = float('inf')
                    self.status_message = f"New goal. Restarting workers. Goal: {goal_str[:50]}"; self._start_new_worker_pool()
                else: self.status_message = "Invalid goal string."
            elif command == 'save': self._save_current_solution(args[0] if args else "default_save")
            elif command == 'load': self._load_named_solution(args[0] if args else "default_save")
            elif command in ['listsaves', 'ls']:
                saves = self._list_saved_solutions()
                self.status_message = "Saved: " + (", ".join(saves) if saves else "None")
            elif command in ['delsave', 'del']: self._delete_saved_solution(args[0] if args else "")
            elif command == 'conf':
                if not args: 
                    self.status_message = "GA Config: (use 'conf <p> [v]')"
                    self.worker_statuses = {i: f"{f.name}: {getattr(self.ga_config, f.name)}" for i,f in enumerate(fields(self.ga_config))}
                elif len(args) == 1: 
                    if hasattr(self.ga_config, args[0]): self.status_message = f"conf.{args[0]} = {getattr(self.ga_config, args[0])}"
                    else: self.status_message = f"Unknown config: {args[0]}"
                elif len(args) >= 2: 
                    p_name, p_val_str = args[0], " ".join(args[1:])
                    if not hasattr(self.ga_config, p_name): self.status_message = f"Unknown config: {p_name}"
                    else:
                        f_type = type(getattr(self.ga_config, p_name))
                        try:
                            if f_type == bool: new_v = p_val_str.lower() in ['true', '1', 'yes']
                            elif f_type == list : new_v = [s.strip() for s in p_val_str.split(',')]
                            else: new_v = f_type(p_val_str)
                            setattr(self.ga_config, p_name, new_v); self._save_ga_config()
                            self.status_message = f"Set conf.{p_name} = {new_v}. Restart workers."
                        except ValueError: self.status_message = f"Invalid value for {p_name} (expected {f_type.__name__})."
            else: self.status_message = f"Unknown cmd: '{command}'. Help: 'h'"
            return True
        elif key_code in [curses.KEY_BACKSPACE, 127, 8]: self.user_input = self.user_input[:-1]
        elif 32 <= key_code <= 126: 
            if self.input_win and len(self.user_input) < (self.input_win.getmaxyx()[1] - 5): self.user_input += chr(key_code)
        return True

    # Inside CursesApp class
    def _process_worker_results(self):
        if not self.results_queue: return

        while not self.results_queue.empty():
            try:
                result_data = self.results_queue.get_nowait()
            except Exception:
                break

            result_type = result_data.get("type")
            worker_id = result_data.get("worker_id", -1) # Use -1 as default if not present

            if result_type == "solution":
                new_solution: GameState = result_data["solution"]
                gen: int = result_data["generation"]
                fitness: float = result_data.get("fitness", float('inf')) # Get fitness, default if missing

                self.current_generation = max(self.current_generation, gen)
                if worker_id != -1 and worker_id in self.worker_statuses: # Check worker_id validity
                    self.worker_statuses[worker_id] = f"Gen {gen}, Best: {fitness:.2f}"

                if fitness < self.best_fitness_so_far:
                    self.best_solution_so_far = new_solution
                    self.best_fitness_so_far = fitness
                    self.status_message = f"New best W{worker_id}! Fit: {fitness:.2f} @G{gen}"
            
            elif result_type == "status":
                 message: str = result_data.get("message", "Unknown status")
                 if worker_id != -1 and worker_id in self.worker_statuses:
                    self.worker_statuses[worker_id] = message
            
            elif result_type == "error":
                message: str = result_data.get("message", "Unknown error from worker.")
                if worker_id != -1 and worker_id in self.worker_statuses:
                    self.worker_statuses[worker_id] = f"CRASHED! Check log." 
                
                self.status_message = f"WORKER {worker_id} CRASHED! See console & worker_{worker_id}_crash.log"
                
                log_file_name = f"worker_{worker_id}_crash.log"
                try:
                    with open(log_file_name, "a") as f_log: 
                        f_log.write(f"\n--- CRASH AT {time.asctime()} ---\n")
                        f_log.write(message)
                        f_log.write("\n-------------------------------\n")
                except Exception as log_e:
                    print(f"Failed to write to worker crash log {log_file_name}: {log_e}", file=sys.stderr)

                print(f"\n--- WORKER {worker_id} CRASH LOG (also in {log_file_name}) ---", file=sys.stderr)
                print(message, file=sys.stderr)
                print(f"--- END WORKER {worker_id} CRASH LOG ---", file=sys.stderr)
                
    def _draw_ui(self): # As before, ensure curses calls are guarded if self.status_win etc. can be None
        if self.windows_need_recreate:
            if not self._init_curses_windows(): return
        if not all([self.status_win, self.worker_status_win, self.input_win]):
             # This case should be handled by _init_curses_windows returning False earlier
            return

        self.status_win.erase(); self.status_win.box()
        self.status_win.addstr(0, 2, " RTS Build Order Optimizer (GA) ", curses.color_pair(1) | curses.A_BOLD) # type: ignore
        
        goal_parts = []
        for act, u_code, count in self.goal_sequence:
            name = UNITS_DATA.get(u_code, {}).get("Name", u_code)
            if act == ACTION_UPGRADE:
                t_name = UNITS_DATA.get(UPGRADE_MAP.get(u_code,"?"),{}).get("Name", UPGRADE_MAP.get(u_code,"?"))
                goal_parts.append(f"{count}x {name}->{t_name}")
            else: goal_parts.append(f"{count}x {name}" if act==ACTION_BUILD else f"{act} {count}x {name}")
        goal_str_disp = " -> ".join(goal_parts)
        max_g_len = self.status_win.getmaxyx()[1] - 10
        self.status_win.addstr(1, 2, f"GOAL: {goal_str_disp[:max_g_len]}", curses.color_pair(3)) # type: ignore

        run_stat_disp = "PAUSED" if self.is_paused else "RUNNING" if self.workers and any(w.is_alive() for w in self.workers) else "IDLE"
        self.status_win.addstr(2, 2, f"Mode: {run_stat_disp} ({len(self.workers)} workers)", curses.color_pair(4)) # type: ignore
        self.status_win.addstr(3, 2, f"Global Best Gen: ~{self.current_generation}", curses.color_pair(5)) # type: ignore

        if self.best_solution_so_far:
            mins, secs = divmod(self.best_solution_so_far.time, 60)
            self.status_win.addstr(4, 2, f"Best Time: {int(mins):02d}:{int(secs):02d}", curses.color_pair(2)) # type: ignore
            self.status_win.addstr(5, 2, f"Best Score: {self.best_fitness_so_far:.2f}", curses.color_pair(2)) # type: ignore
            c_str = f"M Cost: {int(self.best_solution_so_far.total_metal_cost)}"
            w_str = f"Waste M/E: {int(self.best_solution_so_far.wasted_metal)}/{int(self.best_solution_so_far.wasted_energy)}"
            self.status_win.addstr(6, 2, c_str, curses.color_pair(4)) # type: ignore
            self.status_win.addstr(7, 2, w_str, curses.color_pair(4)) # type: ignore
        else: self.status_win.addstr(5, 2, "No solution found yet...", curses.color_pair(3)) # type: ignore
        
        max_stat_msg_len = self.status_win.getmaxyx()[1] - 4
        self.status_win.addstr(8, 2, self.status_message[:max_stat_msg_len], curses.color_pair(3)) # type: ignore

        self.worker_status_win.erase(); self.worker_status_win.box()
        self.worker_status_win.addstr(0, 2, " Worker Status ", curses.color_pair(1) | curses.A_BOLD) # type: ignore
        ws_h, ws_w = self.worker_status_win.getmaxyx()
        y_off = 1 
        for w_id, msg in sorted(self.worker_statuses.items()):
            if y_off >= ws_h -1 : break 
            disp_msg = f"W{w_id}: {msg}"; col_pid = 4 
            if any(s in msg.lower() for s in ["error", "catastrophe"]): col_pid = 6 
            elif any(s in msg.lower() for s in ["hyper", "stagnated"]): col_pid = 3 
            elif any(s in msg.lower() for s in ["found", "best"]): col_pid = 2 
            elif "paused" in msg.lower(): col_pid = 7 
            self.worker_status_win.addstr(y_off, 2, disp_msg[:ws_w-4], curses.color_pair(col_pid)) # type: ignore
            y_off += 1

        self.input_win.erase(); self.input_win.box()
        self.input_win.addstr(1, 2, f"> {self.user_input}") # type: ignore
        self.input_win.move(1, 2 + len(self.user_input) + 2) # type: ignore
        
        self.status_win.noutrefresh(); self.worker_status_win.noutrefresh(); self.input_win.noutrefresh()
        curses.doupdate()         

    def run_main_loop(self):
        """Main application loop managing UI, input, and GA processes."""
        self._init_curses_settings()
        
        if self.windows_need_recreate : self._init_curses_windows()
        self._draw_ui() 

        running = True
        while running:
            try:
                key_code = self.stdscr.getch() 
                
                if key_code != -1: 
                    running = self._handle_input(key_code)
                
                self._process_worker_results()
                
                if self.windows_need_recreate:
                    if not self._init_curses_windows():
                        time.sleep(0.5) 
                        continue 

                self._draw_ui() 
                
                if self.workers and not self.is_paused:
                    active_workers = []
                    workers_were_logically_running = any(w.is_alive() for w in self.workers)

                    for i, worker in enumerate(self.workers):
                        if worker.is_alive():
                            active_workers.append(worker)
                        else:
                            if self.worker_statuses.get(i) not in ["Idle", "Terminating...", "Worker finished."]:
                                self.worker_statuses[i] = "ERROR: Died unexpectedly"
                    self.workers = active_workers
                    
                    if workers_were_logically_running and not any(w.is_alive() for w in self.workers): 
                        self.status_message = "All workers seem to have finished or crashed. Check status."

                time.sleep(0.05) 
            
            except curses.error as e: # type: ignore
                 # Curses errors are ignored by type checker here due to conditional import
                 # but we still want to catch them if they occur.
                 try:
                    self.stdscr.erase()
                    self.stdscr.addstr(0,0, f"A Curses error occurred: {e}. Please try resizing or restarting.")
                    self.stdscr.refresh()
                 except: pass # If stdscr itself is broken
                 time.sleep(2) 
                 self.windows_need_recreate = True 
            except KeyboardInterrupt: 
                self.status_message = "KeyboardInterrupt received. Exiting..."
                running = False
            except Exception as e: 
                try:
                    self.stdscr.erase()
                    import traceback
                    tb_str = traceback.format_exc()
                    with open("ga_optimizer_crash.log", "w") as f_err:
                        f_err.write(f"Unhandled Exception: {e}\n{tb_str}")
                    self.stdscr.addstr(0,0, "An critical error occurred. Check ga_optimizer_crash.log.")
                    self.stdscr.addstr(1,0, str(e)[:self.stdscr.getmaxyx()[1]-1])
                    self.stdscr.refresh()
                    time.sleep(5)
                except: pass # If stdscr is broken
                running = False

        self._stop_all_workers()

# --- main_curses_wrapper and if __name__ == "__main__": (KEEP AS IS from your full script) ---
def main_curses_wrapper(stdscr):
    app = CursesApp(stdscr)
    app.run_main_loop()

if __name__ == "__main__":
    if os.name == 'nt':
        from multiprocessing import freeze_support
        freeze_support() # Call this only once at the beginning

    try:
        curses.wrapper(main_curses_wrapper) # Call this only once
        print("Application closed successfully.")
    except curses.error as e:
        print(f"Curses Initialization/Teardown Error: {e}")
        print("Please ensure your terminal window is large enough and supports colors.")
        print("On Windows, consider using Windows Terminal or a modern terminal emulator.")
    except Exception as e:
        import traceback
        print(f"An unexpected error occurred: {e}") # Simplified for clarity
        traceback.print_exc()