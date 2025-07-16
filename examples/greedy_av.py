import sys
import os

# 1) add your project’s src/ directory to the module search path
sys.path.insert(0, os.path.abspath(os.path.join(__file__, "..", "..", "src")))

# 2) now import everything else
from pabutools.visualisation.visualisation import MESVisualiser
from pabutools.rules.mes import method_of_equal_shares
from pabutools.rules.phragmen import sequential_phragmen
from pabutools import election
from pabutools.election import Cost_Sat
from visualization.av_graph import av_graph

instance, profile = election.parse_pabulib("./examples/netherlands_amsterdam_252_.pb")

av_graph(instance, profile)
