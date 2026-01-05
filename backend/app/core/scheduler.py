from ortools.sat.python import cp_model
from typing import List, Dict, Any
from datetime import date, timedelta

class SchedulingEngine:
    def __init__(self, doctors: List[Any], shift_types: List[Any], start_date: date, num_days: int):
        self.doctors = doctors
        self.shift_types = shift_types
        self.start_date = start_date
        self.num_days = num_days
        self.model = cp_model.CpModel()
        self.shifts = {} # (doctor_id, day_index, shift_id) -> BoolVar
        self.all_days = range(num_days)
        
    def build_model(self):
        # 1. Create Variables
        for d in self.all_days:
            for shift in self.shift_types:
                for doctor in self.doctors:
                    self.shifts[(doctor.id, d, shift.id)] = self.model.NewBoolVar(
                        f'shift_doc{doctor.id}_day{d}_sh{shift.id}'
                    )

        # 2. Hard Constraints
        
        # 2.1 Each shift must be assigned to EXACTLY ONE doctor (simplified for now)
        # In reality, might need N doctors depending on shift config.
        for d in self.all_days:
            for shift in self.shift_types:
                self.model.AddExactlyOne(
                    self.shifts[(doc.id, d, shift.id)] for doc in self.doctors
                )

        # 2.2 Each doctor works at most one shift per day
        for doc in self.doctors:
            for d in self.all_days:
                self.model.AddAtMostOne(
                    self.shifts[(doc.id, d, shift.id)] for shift in self.shift_types
                )
        
        # 2.3 No consecutive "24h" conflicts (Simplified: If night shift D, no day shift D+1)
        # Assuming Shift ID 2 is Night, ID 1 is Day. 
        # Needs flexible logic based on shift definitions.
        # For MVP: If works any shift on Day D, verify rest time? 
        # Let's say: Cannot work on D+1 if worked Night on D.
        night_shifts = [s for s in self.shift_types if "Night" in s.name or "夜" in s.name]
        for doc in self.doctors:
            for d in range(self.num_days - 1):
                for night in night_shifts:
                    # If worked night on day d, cannot work ANY shift on day d+1
                    # (This is a strong constraint, common in hospitals)
                    worked_night = self.shifts[(doc.id, d, night.id)]
                    for next_shift in self.shift_types:
                         self.model.Add(self.shifts[(doc.id, d + 1, next_shift.id)] == 0).OnlyEnforceIf(worked_night)

        # 3. Soft Constraints (Objectives)
        
        # 3.1 Balance number of shifts
        min_shifts_per_doc = (self.num_days * len(self.shift_types)) // len(self.doctors)
        max_shifts_per_doc = min_shifts_per_doc + 2
        
        for doc in self.doctors:
            shifts_worked = []
            for d in self.all_days:
                for s in self.shift_types:
                    shifts_worked.append(self.shifts[(doc.id, d, s.id)])
            
            # Penalize deviation from average
            # This is complex in CP-SAT directly without "AddSoftConstraint". 
            # We minimize the sum of shifts worked * weight? No, we want equality.
            # Simple approach: Minimize (Max - Min) or just Minimize Sum(Overworked)
            
            # Let's just try to keep it within range for now (Hard constraint for MVP balance)
            # self.model.AddLinearConstraint(sum(shifts_worked), min_shifts_per_doc, max_shifts_per_doc)
            pass

    def solve(self):
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)
        
        results = []
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            for d in self.all_days:
                current_date = self.start_date + timedelta(days=d)
                for s in self.shift_types:
                    for doc in self.doctors:
                        if solver.Value(self.shifts[(doc.id, d, s.id)]):
                            results.append({
                                "date": current_date,
                                "doctor_id": doc.id,
                                "shift_type_id": s.id
                            })
            return results
        return None
