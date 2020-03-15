"""
Based on Newson, Paul, and John Krumm. "Hidden Markov map matching through
noise and sparseness." Proceedings of the 17th ACM SIGSPATIAL International
Conference on Advances in Geographic Information Systems. ACM, 2009.
This is a Python translation from https://github.com/graphhopper/map-matching/tree/master/hmm-lib
"""

from ..hmm.hmm_probabilities import HMMProbabilities
from ..hmm.ti_viterbi import ViterbiAlgorithm, SequenceState
from ..map_matcher import MapMatcher
from ..candidate_point import get_candidates
from ...common.spatial_func import distance
from ...common.trajectory import STPoint, Trajectory
from ..utils import find_shortest_path
from ..route_constructor import construct_path


class TimeStep:
    """
    Contains everything the hmm-lib needs to process a new time step including emission and observation probabilities.
    """
    def __init__(self, observation, candidates):
        if observation is None or candidates is None:
            raise Exception('observation and candidates must not be null.')
        self.observation = observation
        self.candidates = candidates
        self.emission_log_probabilities = {}
        self.transition_log_probabilities = {}
        # transition -> dist
        self.road_paths = {}

    def add_emission_log_probability(self, candidate, emission_log_probability):
        if candidate in self.emission_log_probabilities:
            raise Exception('Candidate has already been added.')
        self.emission_log_probabilities[candidate] = emission_log_probability

    def add_transition_log_probability(self, from_position, to_position, transition_log_probability):
        transition = (from_position, to_position)
        if transition in self.transition_log_probabilities:
            raise Exception('Transition has already been added.')
        self.transition_log_probabilities[transition] = transition_log_probability

    def add_road_path(self, from_position, to_position, road_path):
        transition = (from_position, to_position)
        if transition in self.road_paths:
            raise Exception('Transition has already been added.')
        self.road_paths[transition] = road_path


class TIHMMMapMatcher(MapMatcher):
    def __init__(self, rn, routing_weight='length', debug=False):
        self.measurement_error_sigma = 50.0
        self.transition_probability_beta = 2.0
        self.debug = debug
        super(TIHMMMapMatcher, self).__init__(rn, routing_weight)

    # our implementation, no candidates or no transition will be set to None, and start a new matching
    def match(self, traj):
        seq = self.compute_viterbi_sequence(traj.pt_list)
        assert len(traj.pt_list) == len(seq), 'pt_list and seq must have the same size'
        mm_pt_list = []
        for ss in seq:
            candi_pt = None
            if ss.state is not None:
                candi_pt = ss.state
            data = {'candi_pt': candi_pt}
            mm_pt_list.append(STPoint(ss.observation.lat, ss.observation.lng, ss.observation.time, data))
        mm_traj = Trajectory(traj.oid, traj.tid, mm_pt_list)
        return mm_traj

    def match_to_path(self, traj):
        mm_traj = self.match(traj)
        path = construct_path(self.rn, mm_traj, self.routing_weight)
        return path

    def create_time_step(self, pt):
        time_step = None
        candidates = get_candidates(pt, self.rn, self.measurement_error_sigma)
        if candidates is not None:
            time_step = TimeStep(pt, candidates)
        return time_step

    def compute_viterbi_sequence(self, pt_list):
        seq = []
        probabilities = HMMProbabilities(self.measurement_error_sigma, self.transition_probability_beta)
        viterbi = ViterbiAlgorithm(keep_message_history=self.debug)
        prev_time_step = None
        idx = 0
        nb_points = len(pt_list)
        while idx < nb_points:
            time_step = self.create_time_step(pt_list[idx])
            # construct the sequence ended at t-1, and skip current point (no candidate error)
            if time_step is None:
                seq.extend(viterbi.compute_most_likely_sequence())
                seq.append(SequenceState(None, pt_list[idx], None))
                viterbi = ViterbiAlgorithm(keep_message_history=self.debug)
                prev_time_step = None
            else:
                self.compute_emission_probabilities(time_step, probabilities)
                if prev_time_step is None:
                    viterbi.start_with_initial_observation(time_step.observation, time_step.candidates,
                                                           time_step.emission_log_probabilities)
                else:
                    self.compute_transition_probabilities(prev_time_step, time_step, probabilities)
                    viterbi.next_step(time_step.observation, time_step.candidates, time_step.emission_log_probabilities,
                                      time_step.transition_log_probabilities, time_step.road_paths)
                if viterbi.is_broken:
                    # construct the sequence ended at t-1, and start a new matching at t (no transition error)
                    seq.extend(viterbi.compute_most_likely_sequence())
                    viterbi = ViterbiAlgorithm(keep_message_history=self.debug)
                    viterbi.start_with_initial_observation(time_step.observation, time_step.candidates,
                                                           time_step.emission_log_probabilities)
                prev_time_step = time_step
            idx += 1
        if len(seq) < nb_points:
            seq.extend(viterbi.compute_most_likely_sequence())
        return seq

    def compute_emission_probabilities(self, time_step, probabilities):
        for candi_pt in time_step.candidates:
            dist = candi_pt.error
            time_step.add_emission_log_probability(candi_pt, probabilities.emission_log_probability(dist))

    def compute_transition_probabilities(self, prev_time_step, time_step, probabilities):
        linear_dist = distance(prev_time_step.observation, time_step.observation)
        for prev_candi_pt in prev_time_step.candidates:
            for cur_candi_pt in time_step.candidates:
                path_dist, path = find_shortest_path(self.rn, prev_candi_pt, cur_candi_pt, self.routing_weight)
                # invalid transition has no transition probability
                if path is not None:
                    time_step.add_road_path(prev_candi_pt, cur_candi_pt, path)
                    time_step.add_transition_log_probability(prev_candi_pt, cur_candi_pt,
                                                             probabilities.transition_log_probability(path_dist,
                                                                                                      linear_dist))
