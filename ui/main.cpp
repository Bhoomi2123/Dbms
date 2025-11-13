#include <iostream>
#include <fstream>
#include <string>
#include <unordered_map>
#include <vector>
#include <sstream>
#include <algorithm>
#include <chrono>
#include <thread>

#include "httplib.h"
#include "json.hpp"

using namespace std;
using json = nlohmann::json;

struct Slot {
    string day;
    string time;
    string room;
    string faculty;
    string subject;
    string semester;
};

struct Request {
    int priority;       // 1 = Faculty, 2 = Event, 3 = Student
    string requester;
    string room;
    string day;
    string time;
};

vector<Slot> timetable;
vector<string> all_rooms = {"A101", "B201", "Lab1", "Seminar1", "LT-13", "LT-15"};

// Load CSV 
void load_timetable(const string &filename) {
    ifstream file(filename);
    if (!file.is_open()) {
        cerr << "❌ Error opening file: " << filename << endl;
        return;
    }

    string line;
    getline(file, line); 

    while (getline(file, line)) {
        stringstream ss(line);
        Slot s;
        getline(ss, s.day, ',');
        getline(ss, s.time, ',');
        getline(ss, s.room, ',');
        getline(ss, s.faculty, ',');
        getline(ss, s.subject, ',');
        getline(ss, s.semester, ',');
        timetable.push_back(s);
    }

    cout << "✅ Timetable loaded successfully (" << timetable.size() << " entries)\n";
}

// Utility Functions 
bool is_room_occupied(const string &room, const string &day, const string &time) {
    for (auto &s : timetable) {
        if (s.room == room && s.day == day && s.time == time)
            return true;
    }
    return false;
}

vector<string> get_empty_rooms(const string &day, const string &time) {
    vector<string> empty;
    for (auto &r : all_rooms)
        if (!is_room_occupied(r, day, time))
            empty.push_back(r);
    return empty;
}

// OS ALGORITHMS

// Priority Scheduling Algorithm
bool compare_priority(const Request &a, const Request &b) {
    return a.priority < b.priority; 
}

// Banker's Algorithm (Safe State)
bool is_safe_allocation(const string &room, const string &day, const string &time) {
    return !is_room_occupied(room, day, time);
}

// Resource Allocation 
string allocate_room(Request req) {
    if (!is_safe_allocation(req.room, req.day, req.time))
        return "❌ Room already allocated (unsafe state)";

    Slot newSlot = {req.day, req.time, req.room, req.requester, "Reserved", "Special"};
    timetable.push_back(newSlot);
    return "✅ Room allocated safely to " + req.requester;
}

// MAIN FUNCTION 
int main() {
    load_timetable("data/timetable.csv");

    httplib::Server svr;

    // GET 
    svr.Get("/empty", [](const httplib::Request &req, httplib::Response &res) {
        string day = req.get_param_value("day");
        string time = req.get_param_value("time");

        auto empty = get_empty_rooms(day, time);
        json j;
        j["empty_rooms"] = empty;
        res.set_content(j.dump(4), "application/json");
    });

    // POST request
    svr.Post("/request", [](const httplib::Request &req, httplib::Response &res) {
        json input = json::parse(req.body);
        Request reqObj;
        reqObj.priority = input["priority"];
        reqObj.requester = input["requester"];
        reqObj.room = input["room"];
        reqObj.day = input["day"];
        reqObj.time = input["time"];

        string status = allocate_room(reqObj);

        json result;
        result["requester"] = reqObj.requester;
        result["priority"] = reqObj.priority;
        result["status"] = status;
        res.set_content(result.dump(4), "application/json");
    });

    // GET timetable
    svr.Get("/timetable", [](const httplib::Request &, httplib::Response &res) {
        json j = json::array();
        for (auto &s : timetable) {
            j.push_back({
                {"day", s.day},
                {"time", s.time},
                {"room", s.room},
                {"faculty", s.faculty},
                {"subject", s.subject},
                {"semester", s.semester}
            });
        }
        res.set_content(j.dump(4), "application/json");
    });
    cout << "🌐 Classroom Manager running on http://localhost:8080\n";
    svr.listen("0.0.0.0", 8080);
    return 0;
}
