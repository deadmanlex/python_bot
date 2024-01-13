import game_message
import random
from game_message import *
from actions import *
from enum import Enum
import math
class StationType(Enum):
    SHIELD = 1
    TURRET = 2
    HELM = 3
    RADAR = 4


def getAngleToTarget(origin, target):
    x = origin.x
    y = origin.y
    x2 = target.x
    y2 = target.y
    angle = math.atan2(y2 - y, x2 - x)
    return math.degrees(angle)

class PBot:
    def get_stations_by_type(self, station_type:StationType):
        pass

    def get_crew(self):
        pass

    def get_unassigned_stations(self, station_type:StationType):
        pass

    def get_shield_percentage(self):
        pass

    def move_crewMember(self, crew_member:CrewMember, station:Station, station_type:StationType):
        pass

    def rotate_ship(self):
        pass

    def look_at_target(self, vecteur):
        pass

    def look_at_main_target(self):
        pass

    def change_target(self):
        pass

    def getTargetPosition(self):
        pass

    def shoot(self, turret_station:TurretStation):
        pass

    def rotateTurret(self, turret_station:TurretStation, angle: float):
        pass

    def turretLookAt(self, turret_station:TurretStation, target:Vector):
        pass

    def assign_target(self, team_id:str=None):
        pass

    def load_base_info(self, game_message:GameMessage):
        pass

    def get_next_move(self, game_message: GameMessage):
        pass

class CrewManagement:
        stations_info:StationsData
        ship = None
        constants: Constants
        assignedStations = {}
        lastTarget:str = ""
        actions = []
        pbot = None

        def __init__(self,crew:List[CrewMember]):
            self.assignedStations = {crew[i].id:None for i in range(len(crew))}

        def moveCrewMember(self, crew_member, station: Station):
            self.actions.append(CrewMoveAction(crew_member.id, station.gridPosition))

        def getUnassignedStations(self, station_type: StationType):
            return [stations for stations in self.pbot.get_stations_by_type(station_type)  if (stations.id, station_type) not in self.assignedStations.values() ]

        def getClosestCrewMember(self, station: Station, station_type: StationType):
            closest_dist = 100000000
            closest_crew_member = None
            for crew_member in self.pbot.get_crew():
                if self.assignedStations[crew_member.id] is not None:
                    _, station_type = self.assignedStations[crew_member.id]
                    if station_type == StationType.HELM: continue
                if station_type == StationType.SHIELD:
                    if self.assignedStations[crew_member.id] is not None and self.assignedStations[crew_member][1] != StationType.SHIELD:
                        continue
                    for sstat in crew_member.distanceFromStations.shields:
                        if station.id == sstat.stationId:
                            dist = sstat.distance
                elif station_type == StationType.HELM:
                    for sstat in crew_member.distanceFromStations.helms:
                        if station.id == sstat.stationId:
                            dist = sstat.distance
                elif station_type == StationType.TURRET:
                    if self.assignedStations[crew_member.id] is not None and self.assignedStations[crew_member][1] != StationType.TURRET:
                        continue
                    for sstat in crew_member.distanceFromStations.turrets:
                        if station.id == sstat.stationId:
                            dist = sstat.distance
                elif station_type == StationType.RADAR:
                    for sstat in crew_member.distanceFromStations.radars:
                        if station.id == sstat.stationId:
                            dist = sstat.distance
                if dist is not None and closest_dist > dist and dist is not None and dist >= 0:
                    closest_dist = dist
                    closest_crew_member = crew_member
            return closest_crew_member

        def crewDistByType(self, crewMember:CrewMember, station_type):
            if station_type == StationType.SHIELD:
                return crewMember.distanceFromStations.shields
            elif station_type == StationType.HELM:
                return crewMember.distanceFromStations.helms
            elif station_type == StationType.TURRET:
                return crewMember.distanceFromStations.turrets
            elif station_type == StationType.RADAR:
                return  crewMember.distanceFromStations.radars

        def assignClosestCrew(self, station: Station, type:StationType):
            closest_c_member = self.getClosestCrewMember(station, type)
            self.LeaveStation(closest_c_member)
            self.assignCrewMember(closest_c_member, station.id, type)
            self.moveCrewMember(closest_c_member, station)

        def assignIdleCrew(self, station:Station, type:StationType):
            idle_crew = None
            for crew_member in self.ship.crew:
                if idle_crew is not None: break
                if self.assignedStations[crew_member.id] is None:
                    for sstat in self.crewDistByType(crew_member, type):
                        if sstat.stationId == station.id and sstat.distance is None:
                            continue
                        elif sstat.stationId == station.id and sstat.distance is not None:
                            idle_crew = crew_member
                            break
            if idle_crew is not None:
                self.assignCrewMember(idle_crew, station.id, type)
                self.moveCrewMember(idle_crew, station)



        def updateStationList(self, ship:Ship, constants:Constants):
            self.stations_info = ship.stations
            self.ship = ship
            self.constants = constants

        #UTILISER LORSQU'UN CREWMEMBER ARRIVE À UNE STATION
        def assignCrewMember(self,crewMember:CrewMember,id:str,s:StationType):
            if crewMember is None:
                return
            if self.assignedStations[crewMember.id] is not None:
                self.assignedStations[crewMember.id] = None
            self.assignedStations[crewMember.id] = (id,s)

        #UTILISER LORSQU'UN CREWMEMBER PART D'UNE STATION
        def LeaveStation(self,crewMember:CrewMember):
            self.assignedStations[crewMember.id] = None

        def CountAssignedStation(self, station_type):
            if station_type == StationType.SHIELD:
                return len([station for station in self.stations_info.shields if (station.id, StationType.SHIELD)  in self.assignedStations.values()])
            elif station_type == StationType.HELM:
                return len([station for station in self.stations_info.helms if (station.id, StationType.HELM)  in self.assignedStations.values()])
            elif station_type == StationType.TURRET:
                return len([station for station in self.stations_info.turrets if (station.id, StationType.TURRET)  in self.assignedStations.values()])
            elif station_type == StationType.RADAR:
                return len([station for station in self.stations_info.radars if (station.id, StationType.RADAR)  in self.assignedStations.values()])

        def ManageAssignations(self):
            if self.CountAssignedStation(StationType.HELM) == 0:
                self.assignIdleCrew(self.stations_info.helms[0], StationType.HELM)

            if (self.ship.currentShield / self.constants.ship.maxShield) >= 0.80:
                while self.CountAssignedStation(StationType.TURRET) < 3:
                    choose_turret = random.choice(self.getUnassignedStations(StationType.TURRET))
                    self.assignIdleCrew(choose_turret, StationType.TURRET)

            if (self.ship.currentShield / self.constants.ship.maxShield) < 0.20:
                while self.CountAssignedStation(StationType.SHIELD) < 2:
                    choose_shield = random.choice(self.getUnassignedStations(StationType.SHIELD))
                    self.assignIdleCrew(choose_shield, StationType.SHIELD)

        def get_stations_by_id(self, id, station_type):
            if station_type == StationType.SHIELD:
                for station in self.stations_info.shields:
                    if station.id == id:
                        return station
            if station_type == StationType.TURRET:
                for station in self.stations_info.turrets:
                    if station.id == id:
                        return station
            if station_type == StationType.HELM:
                for station in self.stations_info.helms:
                    if station.id == id:
                        return station
            if station_type == StationType.RADAR:
                for station in self.stations_info.radars:
                    if station.id == id:
                        return station

        #CLASSE PRINCIPALE, GÈRE CHACUN DES CREWMEMBERS
        def ManageCrew(self, target:Ship, bot:PBot):
            self.pbot = bot
            self.actions = []
            self.ManageAssignations()
            for id, assignation in self.assignedStations.items():
                # cm = Ship.crew[crewMate]
                if assignation is None: continue
                id, stationType = assignation
                if stationType == StationType.TURRET:
                    station = self.get_stations_by_id(id, StationType.TURRET)
                    angle_to_target = getAngleToTarget(station.worldPosition, target.worldPosition)
                    target_orientation_degree = angle_to_target
                    if int(angle_to_target) != int(station.orientationDegrees) and station.operator is not None:
                        self.pbot.rotateTurret(station, angle_to_target)

                    elif station.charge >= 0 and station.operator is not None:
                        self.actions.append(TurretShootAction(stationId=id))

            return self.actions

class Bot(PBot):
    constants = None
    crew_info = None
    ship_info = None
    stations = None
    current_main_target = None
    enemy_ids = []
    enemy_ships: List[Ship]
    assigned_to_shield: int = 0
    crewManager:CrewManagement = None
    current_turn_actions = []

    def __init__(self):
        print("Initializing your super mega duper bot")

    def get_crew(self):
        return self.ship.crew

    def get_stations_by_type(self, station_type:StationType):
        if station_type == StationType.SHIELD:
            return self.ship.stations.shields
        elif station_type == StationType.HELM:
            return self.ship.stations.radars
        elif station_type == StationType.TURRET:
            return self.ship.stations.turrets
        elif station_type == StationType.RADAR:
            return self.ship.stations.radars

    def get_unassigned_stations(self, station_type:StationType):
        return [stations for stations in self.get_stations_by_type(station_type) if stations.operator == None]

    def get_shield_percentage(self):
        return self.ship.currentShield / self.constants.ship.maxShield


    def move_crewMember(self, crew_member:CrewMember, station:Station, station_type:StationType):
        self.current_turn_actions.append(CrewMoveAction(crew_member.id, station.gridPosition))

    def rotate_ship(self):
        target_angle = getAngleToTarget(self.ship.worldPosition, self.enemy_ships[self.current_main_target].worldPosition)
        if self.ship.orientationDegrees != target_angle:
            difference = self.ship.orientationDegrees - target_angle
            if difference > self.constants.ship.maxRotationDegrees:
                self.current_turn_actions.append(ShipRotateAction(self.constants.ship.maxRotationDegrees if difference > 0 else - self.constants.ship.maxRotationDegrees))
            else:
                self.current_turn_actions.append(ShipRotateAction(difference))

    def look_at_target(self, vecteur):
        self.current_turn_actions.append(ShipLookAtAction(vecteur))

    def look_at_main_target(self):
        self.look_at_target(self.enemy_ships[self.current_main_target].worldPosition)

    def change_target(self):
        current_main_target = self.enemy_ids.index() + 1

    def getTargetPosition(self):
        if self.current_main_target != None:
            return game_message.shipsPositions.get(self.current_main_target)

    def shoot(self, turret_station:TurretStation):
        self.current_turn_actions.append(TurretShootAction(stationId=turret_station.id))

    def rotateTurret(self, turret_station:TurretStation, angle:float):
        if turret_station.turretType == TurretType.Normal or turret_station.turretType == TurretType.EMP:
            target_angle = getAngleToTarget(self.ship.worldPosition, self.enemy_ships[self.current_main_target].worldPosition)
            if turret_station.orientationDegrees != target_angle:
                difference = turret_station.orientationDegrees - target_angle
                if difference > self.constants.ship.maxRotationDegrees:
                    self.current_turn_actions.append(TurretRotateAction(stationId=turret_station.id, angle=self.constants.ship.maxRotationDegrees if difference > 0 else -self.constants.ship.maxRotationDegrees))
                else:
                    self.current_turn_actions.append(TurretRotateAction(stationId=turret_station.id, angle=difference))

    def turretLookAt(self, turret_station:TurretStation, target:Vector):
        if turret_station.turretType == TurretType.Normal or turret_station.turretType == TurretType.EMP:
            self.current_turn_actions.append(TurretLookAtAction(turret_station.id, target=target))

    def assign_target(self, team_id:str=None):
        if team_id == None:
            self.current_main_target = self.enemy_ids[0]

    def load_base_info(self, game_message:GameMessage):
        id = game_message.currentTeamId
        self.ship = game_message.ships[id]
        self.crew_info = game_message.ships[id].crew
        self.stations = game_message.ships[id].stations
        self.enemy_ships = {}
        self.enemy_ids = []
        self.constants = game_message.constants
        for teams_ids in game_message.ships.keys():
            if teams_ids is not game_message.currentTeamId:
                self.enemy_ids.append(teams_ids)
                self.enemy_ships[teams_ids] = game_message.ships[teams_ids]

    def get_next_move(self, game_message: GameMessage):
        """
        Here is where the magic happens, for now the moves are not very good. I bet you can do better ;)
        """
        self.load_base_info(game_message)
        if self.crewManager == None: self.crewManager = CrewManagement(self.ship.crew)
        self.crewManager.updateStationList(self.ship, self.constants)
        self.assign_target()
        team_id = game_message.currentTeamId
        my_ship = game_message.ships.get(team_id)
        other_ships_ids = [shipId for shipId in game_message.shipsPositions.keys() if shipId != team_id]
        self.current_turn_actions.extend(self.crewManager.ManageCrew(game_message.ships[self.current_main_target], self))

        # You can clearly do better than the random actions above! Have fun!
        return self.current_turn_actions

