class Applicant:
    def __init__(self, name: str, rankings: list[str]):
        self.name: str = name
        self.residency_rankings: list[str] = rankings
        self.remaining_ranked_residencies: list[str] = rankings
        self.tentative_match: Residency | None = None

    def __repr__(self):
        return f"Applicant(name={self.name}, rankings_count={len(self.remaining_ranked_residencies)})"
    

class Residency:
    
    def __init__(self, name: str, rankings: list[str], total_positions: int):
        self.name: str = name
        self.applicant_rankings: list[str] = rankings
        self.assigned_applicants: dict[str, tuple[Applicant, int]] = {}
        self.total_positions: int = total_positions
        self.positions_available: int = total_positions
        self.least_preferred_match: tuple[Applicant, int] | None = None

    def __repr__(self):
        return f"Residency(name={self.name}, rankings_count={len(self.applicant_rankings)})"
    

def try_match_applicant_to_residency(applicant: Applicant, residency: Residency) -> Applicant | None:
    if applicant.name not in residency.applicant_rankings: 
        # if not in residency ranking, bail
        return None
    
    if residency.name not in applicant.remaining_ranked_residencies: 
        # if not in applicant ranking, bail
        return None

    if applicant.tentative_match is not None:
        # if the applicant is already matched, bail
        return None
    
    applicant_rank = residency.applicant_rankings.index(applicant.name)
    if applicant_rank == -1: # if the program didn't rank the applicant, bail
        return None
    
    bumped_match = None
    if residency.positions_available == 0:
        if residency.least_preferred_match is None:
            pass
        (least_preferred_match, least_preferred_match_rank) = residency.least_preferred_match
        if applicant_rank >= least_preferred_match_rank:
            # the current resident is more preferred than the applicant, bail
            return None
        else:
            bumped_match = least_preferred_match
            remove_applicant_from_residency(least_preferred_match, residency)

    applicant.tentative_match = residency
    residency.positions_available -= 1
    residency.assigned_applicants[applicant.name] = (applicant, applicant_rank)
    residency.least_preferred_match = max(residency.assigned_applicants.values(), key=lambda x: x[1])

    return bumped_match


def remove_applicant_from_residency(applicant: Applicant, residency: Residency):
    residency.positions_available += 1
    residency.assigned_applicants.pop(applicant.name)
    applicant.tentative_match = None
    applicant.remaining_ranked_residencies.remove(residency.name)


def run_match(applicants: list[Applicant], residencies: list[Residency]):
    applicants = [applicant for applicant in applicants if applicant.residency_rankings]
    residencies = [residency for residency in residencies if residency.positions_available > 0]

    residencies_map: dict[str, Residency] = {residency.name: residency for residency in residencies}

    applicants_queue = list(applicants)

    while applicants_queue:
        applicant = applicants_queue.pop(0)
        if applicant.tentative_match is not None:
            continue

        # find the highest ranked residency that the ranks the applicant
        for residency_name in applicant.remaining_ranked_residencies:
            bumped_applicant = try_match_applicant_to_residency(applicant, residencies_map[residency_name])
            if bumped_applicant is not None:
                applicants_queue.append(bumped_applicant)
            if applicant.tentative_match is not None:
                # the applicant just got matched
                break

