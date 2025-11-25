import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(__file__, "..", "..", "src")))

from pabutools.visualisation.visualisation import MESVisualiser
from pabutools.rules.mes import method_of_equal_shares
from pabutools.rules.phragmen import sequential_phragmen
from pabutools import election
from pabutools.election import Cost_Sat
from pb_robustness_measures.visualization.av_graph import av_graph
from pb_robustness_measures.rules.greedyAV import greedy_av

instance, profile = election.parse_pabulib("netherlands_amsterdam_252_.pb")
print(len(greedy_av(instance, profile)))
