from abc import abstractmethod
from datetime import timedelta, datetime


class MakeDate:
    @staticmethod
    def make_date(date_time_str):
        date_time_str = ' '.join(date_time_str.split())
        dt = datetime.strptime(date_time_str, "%H:%M:%S %Y.%m.%d")
        return dt

    @staticmethod
    def zero():
        return MakeDate.make_date("00:00:00 2019.11.26")


class Station:
    Name_Station = "Astrakhan"
    number_of_path = 3
    ways = {i: MakeDate.zero() for i in range(1, number_of_path+1)}
    sum_information = []

    @staticmethod
    def create_events():
        with open("input.txt", "r") as data:
            lines_information = []
            for line in data:
                lines_information.append(list(map(str, line.strip("\n").split(";"))))

        for line in lines_information:
            if line[0] == "Passing train":
                train = PassingTrain(line[1], line[2], line[3], int(line[4]), line[5], line[6], line[7])
                train.assign_way()
                train.arrival_train()
                train.departure_train()
            elif line[0] == "Formed Train":
                formed_train = FormedTrain(line[1], line[2], line[3], int(line[4]), line[5], line[6], line[7])
                formed_train.assign_way()
                formed_train.departure_train()
            elif line[0] == "Hitching wagons":
                train_wagons = TrainWagons(line[1], line[2], line[3], int(line[4]), line[5], int(line[6]), line[7])
                train_wagons.wagons_hitching()
            elif line[0] == "Uncoupling wagons":
                train_wagons = TrainWagons(line[1], line[2], line[3], int(line[4]), line[5], int(line[6]), line[7])
                train_wagons.wagons_uncoupling()

        return sorted(Station.sum_information, key=lambda event: event.event_date)


class Train:
    def __init__(self, train_id, route_from, route_to, num_of_wagons, numbering_direction):
        self.train_id = train_id
        self.route_from = route_from
        self.route_to = route_to
        self.num_of_wagons = num_of_wagons
        self.numbering_direction = numbering_direction


class PassingTrain(Train):
    def __init__(self, train_id, route_from, route_to, num_of_wagons, numbering_direction,
                 arriving_time, departing_time):
        super().__init__(train_id, route_from, route_to, num_of_wagons, numbering_direction)
        self.arriving_time = MakeDate.make_date(arriving_time)
        self.departing_time = MakeDate.make_date(departing_time)
        self.way_for_train = 0

    def assign_way(self):
        for way in Station.ways:
            if (Station.ways[way] == MakeDate.zero()) or (Station.ways[way] <= self.arriving_time):
                Station.ways[way] = self.departing_time
                self.way_for_train = way
                way_assignment = WayAssignment(self.train_id, self.route_from, self.route_to, self.num_of_wagons,
                                               self.numbering_direction, self.arriving_time, self.departing_time,
                                               self.way_for_train)
                Station.sum_information.append(way_assignment)
                break

    def arrival_train(self):
        train_arrival = TrainArrival(self.train_id, self.route_from, self.route_to, self.num_of_wagons,
                                     self.numbering_direction, self.arriving_time, self.departing_time,
                                     self.way_for_train)
        Station.sum_information.append(train_arrival)

    def departure_train(self):
        train_departure = TrainDeparture(self.train_id, self.route_from, self.route_to, self.num_of_wagons,
                                         self.numbering_direction, self.arriving_time, self.departing_time,
                                         self.way_for_train)
        Station.sum_information.append(train_departure)


class FormedTrain(PassingTrain):
    def assign_way(self):
        for way in Station.ways:
            if (Station.ways[way] == MakeDate.zero()) or (Station.ways[way] <= self.arriving_time):
                Station.ways[way] = self.departing_time
                self.way_for_train = way
                way_assignment_for_formed_train = WayAssignmentForFormedTrain(self.train_id, self.route_from,
                                                                              self.route_to, self.num_of_wagons,
                                                                              self.numbering_direction,
                                                                              self.arriving_time, self.departing_time,
                                                                              self.way_for_train)
                Station.sum_information.append(way_assignment_for_formed_train)
                break

    def departure_train(self):
        train_departure = TrainDeparture(self.train_id, self.route_from, self.route_to, self.num_of_wagons,
                                         self.numbering_direction, self.arriving_time, self.departing_time,
                                         self.way_for_train)
        Station.sum_information.append(train_departure)


class TrainWagons(Train):
    def __init__(self, train_id, route_from, route_to, num_of_wagons, numbering_direction,
                 num_of_changed_wagons, changed_wagons_time):
        super().__init__(train_id, route_from, route_to, num_of_wagons, numbering_direction)
        self.num_of_changed_wagons = num_of_changed_wagons
        self.changed_wagons_time = MakeDate.make_date(changed_wagons_time)

    def wagons_hitching(self):
        hitching_wagons = HitchingWagons(self.train_id, self.route_from, self.route_to, self.num_of_wagons,
                                         self.numbering_direction, self.num_of_changed_wagons, self.changed_wagons_time)
        Station.sum_information.append(hitching_wagons)
        self.num_of_wagons += self.num_of_changed_wagons

    def wagons_uncoupling(self):
        uncoupling_wagons = UncouplingWagons(self.train_id, self.route_from, self.route_to, self.num_of_wagons,
                                             self.numbering_direction, self.num_of_changed_wagons,
                                             self.changed_wagons_time)
        Station.sum_information.append(uncoupling_wagons)
        self.num_of_wagons -= self.num_of_changed_wagons


class Event(Train):
    def __init__(self, train_id, route_from, route_to, num_of_wagons, numbering_direction):
        super().__init__(train_id, route_from, route_to, num_of_wagons, numbering_direction)
        self.event_date = MakeDate.zero()

    @abstractmethod
    def display_information(self):
        pass

    def __repr__(self):
        return repr(self.event_date)


class WayAssignment(Event):
    local_time = timedelta(minutes=10)

    def __init__(self, train_id, route_from, route_to, num_of_wagons, numbering_direction,
                 arriving_time, departing_time, way_for_train):
        super().__init__(train_id, route_from, route_to, num_of_wagons, numbering_direction)
        self.arriving_time = arriving_time
        self.departing_time = departing_time
        self.way_for_train = way_for_train
        self.event_date = self.arriving_time - WayAssignment.local_time

    def display_information(self):
        print(f"{self.event_date}: Назначен путь {self.way_for_train} для поезда {self.train_id}. "
              f"Нумерация поезда: {self.numbering_direction}")


class WayAssignmentForFormedTrain(WayAssignment, Event):
    def display_information(self):
        print(f"{self.event_date}: Назначен путь {self.way_for_train} для сформированного на станции поезда "
              f"{self.train_id}. Нумерация поезда: {self.numbering_direction}")


class TrainArrival(Event):
    def __init__(self, train_id, route_from, route_to, num_of_wagons, numbering_direction,
                 arriving_time, departing_time, way_for_train):
        super().__init__(train_id, route_from, route_to, num_of_wagons, numbering_direction)
        self.arriving_time = arriving_time
        self.departing_time = departing_time
        self.way_for_train = way_for_train
        self.event_date = self.arriving_time

    def display_information(self):
        print(f"{self.event_date}: Прибыл поезд {self.train_id} на путь {self.way_for_train}")


class TrainDeparture(Event):
    def __init__(self, train_id, route_from, route_to, num_of_wagons, numbering_direction,
                 arriving_time, departing_time, way_for_train):
        super().__init__(train_id, route_from, route_to, num_of_wagons, numbering_direction)
        self.arriving_time = arriving_time
        self.departing_time = departing_time
        self.way_for_train = way_for_train
        self.event_date = self.departing_time

    def display_information(self):
        print(f"{self.event_date}: Отправился поезд {self.train_id} с пути {self.way_for_train}")


class HitchingWagons(Event):
    def __init__(self, train_id, route_from, route_to, num_of_wagons, numbering_direction,
                 num_of_changed_wagons, changed_wagons_time):

        super().__init__(train_id, route_from, route_to, num_of_wagons, numbering_direction)
        self.num_of_changed_wagons = num_of_changed_wagons
        self.changed_wagons_time = changed_wagons_time
        self.event_date = self.changed_wagons_time

    def display_information(self):
        print(f"{self.event_date}: Прицепение вагонов в количестве {self.num_of_changed_wagons} "
              f"к поезду {self.train_id}. Количество вагонов в поезде: "
              f"{self.num_of_wagons + self.num_of_changed_wagons}")


class UncouplingWagons(Event):
    def __init__(self, train_id, route_from, route_to, num_of_wagons, numbering_direction,
                 num_of_changed_wagons, changed_wagons_time):
        super().__init__(train_id, route_from, route_to, num_of_wagons, numbering_direction)
        self.num_of_changed_wagons = num_of_changed_wagons
        self.changed_wagons_time = changed_wagons_time
        self.event_date = self.changed_wagons_time

    def display_information(self):
        print(f"{self.event_date}: Отцепление вагонов в количестве {self.num_of_changed_wagons} "
              f"от поезда {self.train_id}. Количество вагонов в поезде: "
              f"{self.num_of_wagons - self.num_of_changed_wagons}")


if __name__ == "__main__":
    station = Station()
    result_events = station.create_events()
    for i in range(len(result_events)):
        result_events[i].display_information()
