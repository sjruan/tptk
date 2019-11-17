"""
Implementation of the Viterbi algorithm for time-inhomogeneous Markov processes,
meaning that the set of states and state transition probabilities are not necessarily fixed for all time steps.
For long observation sequences, back pointers usually converge to a single path after a
certain number of time steps. For instance, when matching GPS coordinates to roads, the last
GPS positions in the trace usually do not affect the first road matches anymore.
This implementation exploits this fact by letting the Java garbage collector
take care of unreachable back pointers. If back pointers converge to a single path after a
constant number of time steps, only O(t) back pointers and transition descriptors need to be stored in memory.
"""


class ExtendedState:
    """
    Back pointer to previous state candidate in the most likely sequence.
    """
    def __init__(self, state, back_pointer, observation, transition_descriptor):
        self.state = state
        self.back_pointer = back_pointer
        self.observation = observation
        self.transition_descriptor = transition_descriptor


class SequenceState:
    def __init__(self, state, observation, transition_descriptor):
        self.state = state
        self.observation = observation
        self.transition_descriptor = transition_descriptor


class ForwardStepResult:
    def __init__(self):
        """
        Includes back pointers to previous state candidates for retrieving the most likely sequence after the forward pass.
        :param nb_states:
        """
        self.new_message = {}
        self.new_extended_states = {}


class ViterbiAlgorithm:
    def __init__(self, keep_message_history=False):
        # Allows to retrieve the most likely sequence using back pointers.
        self.last_extended_states = None
        self.prev_candidates = []
        # For each state s_t of the current time step t, message.get(s_t) contains the log
        # probability of the most likely sequence ending in state s_t with given observations o_1, ..., o_t.
        #
        # Formally, this is max log p(s_1, ..., s_t, o_1, ..., o_t) w.r.t. s_1, ..., s_{t-1}.
        # Note that to compute the most likely state sequence, it is sufficient and more
        # efficient to compute in each time step the joint probability of states and observations
        # instead of computing the conditional probability of states given the observations.
        # state -> float
        self.message = None
        self.is_broken = False
        # list of message
        self.message_history = None
        if keep_message_history:
            self.message_history = []

    def initialize_state_probabilities(self, observation, candidates, initial_log_probabilities):
        """
        Use only if HMM only starts with first observation.
        :param observation:
        :param candidates:
        :param initial_log_probabilities:
        :return:
        """
        if self.message is not None:
            raise Exception('Initial probabilities have already been set.')
        # Set initial log probability for each start state candidate based on first observation.
        # Do not assign initial_log_probabilities directly to message to not rely on its iteration order.
        initial_message = {}
        for candidate in candidates:
            if candidate not in initial_log_probabilities:
                raise Exception('No initial probability for {}'.format(candidate))
            log_probability = initial_log_probabilities[candidate]
            initial_message[candidate] = log_probability
        self.is_broken = self.hmm_break(initial_message)
        if self.is_broken:
            return
        self.message = initial_message
        if self.message_history is not None:
            self.message_history.append(self.message)
        self.last_extended_states = {}
        for candidate in candidates:
            self.last_extended_states[candidate] = ExtendedState(candidate, None, observation, None)
        self.prev_candidates = [candidate for candidate in candidates]

    def hmm_break(self, message):
        """
        Returns whether the specified message is either empty or only contains state candidates with zero probability and thus causes the HMM to break.
        :return:
        """
        for log_probability in message.values():
            if log_probability != float('-inf'):
                return False
        return True

    def forward_step(self, observation, prev_candidates, cur_candidates, message, emission_log_probabilities,
                     transition_log_probabilities, transition_descriptors=None):
        result = ForwardStepResult()
        assert len(prev_candidates) != 0

        for cur_state in cur_candidates:
            max_log_probability = float('-inf')
            max_prev_state = None
            for prev_state in prev_candidates:
                log_probability = message[prev_state] + self.transition_log_probability(prev_state, cur_state,
                                                                                        transition_log_probabilities)
                if log_probability > max_log_probability:
                    max_log_probability = log_probability
                    max_prev_state = prev_state
            # throws KeyError if cur_state not in the emission_log_probabilities
            result.new_message[cur_state] = max_log_probability + emission_log_probabilities[cur_state]
            # Note that max_prev_state == None if there is no transition with non-zero probability.
            # In this case cur_state has zero probability and will not be part of the most likely
            # sequence, so we don't need an ExtendedState.
            if max_prev_state is not None:
                transition = (max_prev_state, cur_state)
                if transition_descriptors is not None:
                    transition_descriptor = transition_descriptors[transition]
                else:
                    transition_descriptor = None
                extended_state = ExtendedState(cur_state, self.last_extended_states[max_prev_state], observation,
                                               transition_descriptor)
                result.new_extended_states[cur_state] = extended_state
        return result

    def transition_log_probability(self, prev_state, cur_state, transition_log_probabilities):
        transition = (prev_state, cur_state)
        if transition not in transition_log_probabilities:
            return float('-inf')
        else:
            return transition_log_probabilities[transition]

    def most_likely_state(self):
        # Retrieves the first state of the current forward message with maximum probability.
        assert len(self.message) != 0

        result = None
        max_log_probability = float('-inf')
        for state in self.message:
            if self.message[state] > max_log_probability:
                result = state
                max_log_probability = self.message[state]
        # Otherwise an HMM break would have occurred.
        assert result is not None
        return result

    def retrieve_most_likely_sequence(self):
        # Otherwise an HMM break would have occurred and message would be null.
        assert len(self.message) != 0

        last_state = self.most_likely_state()
        # Retrieve most likely state sequence in reverse order
        result = []
        es = self.last_extended_states[last_state]
        while es is not None:
            ss = SequenceState(es.state, es.observation, es.transition_descriptor)
            result.append(ss)
            es = es.back_pointer
        result.reverse()
        return result

    def start_with_initial_observation(self, observation, candidates, emission_log_probabilities):
        """
        Lets the HMM computation start at the given first observation and uses the given emission
        probabilities as the initial state probability for each starting state s.
        :param observation:
        :param candidates:
        :param emission_log_probabilities:
        :return:
        """
        self.initialize_state_probabilities(observation, candidates, emission_log_probabilities)

    def next_step(self, observation, candidates, emission_log_probabilities, transition_log_probabilities, transition_descriptors=None):
        if self.message is None:
            raise Exception('start_with_initial_observation() must be called first.')
        if self.is_broken:
            raise Exception('Method must not be called after an HMM break.')
        forward_step_result = self.forward_step(observation, self.prev_candidates, candidates, self.message,
                                                emission_log_probabilities, transition_log_probabilities, transition_descriptors)
        self.is_broken = self.hmm_break(forward_step_result.new_message)
        if self.is_broken:
            return
        if self.message_history is not None:
            self.message_history.append(forward_step_result.new_message)
        self.message = forward_step_result.new_message
        self.last_extended_states = forward_step_result.new_extended_states
        self.prev_candidates = [candidate for candidate in candidates]

    def compute_most_likely_sequence(self):
        """
        Returns the most likely sequence of states for all time steps. This includes the initial
        states / initial observation time step. If an HMM break occurred in the last time step t,
        then the most likely sequence up to t-1 is returned. See also {@link #isBroken()}.
        Formally, the most likely sequence is argmax p([s_0,] s_1, ..., s_T | o_1, ..., o_T)
        with respect to s_1, ..., s_T, where s_t is a state candidate at time step t,
        o_t is the observation at time step t and T is the number of time steps.
        :return:
        """
        if self.message is None:
            # Return empty most likely sequence if there are no time steps or if initial observations caused an HMM break.
            return []
        else:
            return self.retrieve_most_likely_sequence()
