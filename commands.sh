# The tangle resolution script contains some manual steps so it can't be run as-is from start to end.
# You should run the commands one block at a time and stop at the manual steps
# You first need these files:
# assemblygraph.gfa: An assembly graph for recruiting HiFi reads
# assemblygraph_contigs.txt: A text file with the node IDs of the tangle you want to solve. One node ID per line.
# assemblygraph_contigs_surroundings.txt: A text file with the node IDs of the tangle you want to solve, and the nodes around the tangle. At least 1 Mbp, ideally the entire component. One node ID per line.
# hifi.fa: genome wide HiFi reads
# ONT.fa: genome wide ONT reads

cp assemblygraph_contigs.txt picked.txt
grep -P '^S' < assemblygraph.gfa | awk '{print ">" $2; print $3;}' | scripts/pick_reads_stdin.py > contigs.fa
mummer -maxmatch -l 500 -b -threads 40 contigs.fa hifi.fa > mums.txt
scripts/pick_readnames_with_mums.py < mums.txt > picked_hifi_round1.txt
cp picked_hifi_round1.txt picked.txt
scripts/pick_reads_stdin.py < hifi.fa | gzip > recruited_hifi_hpc.fa.gz
bin/MBG recruited_hifi_hpc.fa.gz graph-hpc-recruitment.gfa 1000 501 1 3
grep -P '^S' < graph-hpc-recruitment.gfa | awk '{print ">" $2; print $3;}' > contigs_one.fa
mummer -maxmatch -l 500 -b -threads 40 contigs_one.fa hifi.fa > mums.txt
scripts/pick_readnames_with_mums.py < mums.txt > picked_hifi_round2.txt
cp picked_hifi_round2.txt picked.txt
scripts/pick_reads_stdin.py < hifi.fa > recruited_hifi_hpc_round2.fa
bin/MBG recruited_hifi_hpc_round2.fa correctiongraph-hpc.gfa 2000 150 1 3
sed 's/\b0\b/1000001/g' < correctiongraph-hpc.gfa | awk 'NR==1{print "H\tVN:Z:1.0"}{print;}' > correctiongraph-hpc-fix0.gfa
/usr/bin/time -v bin/gimbricate -g correctiongraph-hpc-fix0.gfa -n -p contigs.paf -f contigs.fasta > correctiongraph.gimbry.gfa 2> stderr_gimbricate.txt
/usr/bin/time -v bin/seqwish -s contigs.fasta -p contigs.paf -g correctiongraph-seqwished.gfa 2> stderr_seqwish.txt
scripts/unitigify_assembly.py correctiongraph-seqwished.gfa correctiongraph-seqwished-unitig.gfa /dev/null
bin/vg view -Fv correctiongraph-seqwished-unitig.gfa | bin/vg mod -n -U 10 - | bin/vg view - > correctiongraph-seqwished-unitig-normal.gfa
scripts/unitigify_assembly.py correctiongraph-seqwished-unitig-normal.gfa correctiongraph-seqwished-unitig-normal-unitig.gfa /dev/null
/usr/bin/time -v bin/GraphAligner -g correctiongraph-seqwished-unitig-normal-unitig.gfa -f recruited_hifi_hpc_round2.fa -a alns-hifi-correction.gaf -t 40 --seeds-first-full-rows 64 -b 35 1> stdout_ga_hifi_correction.txt 2> stderr_ga_hifi_correction.txt
scripts/extract_extended_path.py correctiongraph-seqwished-unitig-normal-unitig.gfa < alns-hifi-correction.gaf > hifi_corrected.fa

#########################################
#
# Manual step 1: Pick k-mer size for building the repeat collapsed graph
#
# Run these scripts:
bin/MBG hifi_corrected.fa graph-hpc-k3000.gfa 3000 150 1 3 &
bin/MBG hifi_corrected.fa graph-hpc-k3500.gfa 3500 150 1 3 &
bin/MBG hifi_corrected.fa graph-hpc-k4000.gfa 4000 150 1 3 &
bin/MBG hifi_corrected.fa graph-hpc-k4500.gfa 4500 150 1 3 &
bin/MBG hifi_corrected.fa graph-hpc-k5000.gfa 5000 150 1 3 &
bin/MBG hifi_corrected.fa graph-hpc-k5500.gfa 5500 150 1 3 &
bin/MBG hifi_corrected.fa graph-hpc-k6000.gfa 6000 150 1 3 &
bin/MBG hifi_corrected.fa graph-hpc-k6500.gfa 6500 150 1 3 &
bin/MBG hifi_corrected.fa graph-hpc-k7000.gfa 7000 150 1 3 &
bin/MBG hifi_corrected.fa graph-hpc-k7500.gfa 7500 150 1 3 &
bin/MBG hifi_corrected.fa graph-hpc-k8000.gfa 8000 150 1 3 &
bin/MBG hifi_corrected.fa graph-hpc-k8500.gfa 8500 150 1 3 &
bin/MBG hifi_corrected.fa graph-hpc-k9000.gfa 9000 150 1 3 &
bin/MBG hifi_corrected.fa graph-hpc-k9500.gfa 9500 150 1 3 &
bin/MBG hifi_corrected.fa graph-hpc-k10000.gfa 10000 150 1 3 &
bin/MBG hifi_corrected.fa graph-hpc-k11000.gfa 11000 150 1 3 &
bin/MBG hifi_corrected.fa graph-hpc-k12000.gfa 12000 150 1 3 &
bin/MBG hifi_corrected.fa graph-hpc-k13000.gfa 13000 150 1 3 &
bin/MBG hifi_corrected.fa graph-hpc-k14000.gfa 14000 150 1 3 &
bin/MBG hifi_corrected.fa graph-hpc-k15000.gfa 15000 150 1 3 &
#
# Look at the graphs "graph-hpc-k____.gfa" in bandage.
# The goal is to find the highest k where the graph is still in one component.
# Also look for "tips pointing at each other" pattern like this:
#
#              /            \
#             /              \
# -----------   ------------   -------------
# 2x coverage   1x coverage   2x coverage
#
# This happens when one of the unique sequences has missing k-mers in the middle.
# If that happens, pick a lower k.
# Pick the highest k where the graph is still fine.
# Then copy that to graph-hpc.gfa
cp graph-hpc-k4000.gfa graph-hpc.gfa
#
# You can also run the above scripts with other k values.
#
########################################

sed 's/\b0\b/1000001/g' < graph-hpc.gfa | awk 'NR==1{print "H\tVN:Z:1.0"}{print;}' > graph-hpc-fix0.gfa
/usr/bin/time -v bin/gimbricate -g graph-hpc-fix0.gfa -n -p contigs.paf -f contigs.fasta > graph.gimbry.gfa 2> stderr_gimbricate.txt
/usr/bin/time -v bin/seqwish -s contigs.fasta -p contigs.paf -g graph-seqwished.gfa 2> stderr_seqwish.txt
scripts/unitigify_assembly.py graph-seqwished.gfa graph-seqwished-unitig.gfa /dev/null
bin/vg view -Fv graph-seqwished-unitig.gfa | bin/vg mod -n -U 10 - | bin/vg view - > graph-seqwished-unitig-normal.gfa
scripts/unitigify_assembly.py graph-seqwished-unitig-normal.gfa graph-seqwished-unitig-normal-unitig.gfa /dev/null
scripts/indel_to_bubble.py < graph-seqwished-unitig-normal-unitig.gfa > graph-seqwished-unitig-normal-unitig-indelbubble.gfa
/usr/bin/time -v bin/GraphAligner -g graph-seqwished-unitig-normal-unitig-indelbubble.gfa -f recruited_hifi_hpc_round2.fa -a alns-CCS.gaf -t 40 --seeds-first-full-rows 64 -b 35 1> stdout_ga_ccs.txt 2> stderr_ga_ccs.txt
sed 's/id:f://g' < alns-CCS.gaf | awk '{if ($15 > 0.98) print;}' | scripts/calculate_coverage.py graph-seqwished-unitig-normal-unitig-indelbubble.gfa > node_covs.csv
awk '$1!="node"{if ($3 > 35 && $3 < 60 && $2 > 1000) print $1;}' < node_covs.csv > unique_nodes_hifi_automatic.txt
awk '$1!="node"{if ($3 > 40 && $3 < 45) print $1;}' < node_covs.csv >> unique_nodes_hifi_automatic.txt
cp unique_nodes_hifi_automatic.txt unique_nodes_hifi_manual.txt


##############################
#
# Manual step 2: Fix the predicted unique nodes.
#
# The file unique_nodes_hifi_manual.txt has predictions of unique nodes.
# Open graph-seqwished-unitig-normal-unitig-indelbubble.gfa and node_covs.csv with bandage
# and remove false positives from unique_nodes_hifi_manual.txt
# and add false negatives to unique_nodes_hifi_manual.txt.
# Any extra unique nodes will lead to misassembly, and any missing unique nodes
# can lead to a tangle staying unresolved.
#
#############################


sed 's/id:f://g' < alns-CCS.gaf | awk -F '\t' '{if ($15 > 0.98) print $6;}' > paths_hifi_confident.txt
scripts/find_bridges.py unique_nodes_hifi_manual.txt < paths_hifi_confident.txt > uniq_bridges_hifi_all.txt
grep -v '(' < uniq_bridges_hifi_all.txt | grep -vP '^$' | scripts/remove_wrong_connections.py | sort > bridging_seq_hifi_all.txt
scripts/pick_majority_bridge.py < bridging_seq_hifi_all.txt > bridging_seq_hifi_picked.txt 
cp bridging_seq_hifi_picked.txt bridging_seq_hifi_filtered.txt


##############################
#
# Manual step 3: Remove HiFi false bridges.
#
# The file bridging_seq_hifi_filtered.txt has bridges connecting unique nodes.
# Run this script:
scripts/get_clean_connections.py bridging_seq_hifi_filtered.txt | less
# and look at the part "Nodes with extra connections".
# Open graph-seqwished-unitig-normal-unitig-indelbubble.gfa with bandage and find the area.
# Find the unique nodes enclosing the tangle with extra connections,
# edit "subset.txt" and add the node IDs there.
# Then run this script:
scripts/find_bridges.py subset.txt < bridging_seq_hifi_filtered.txt | less
# and scroll to the end.
# It will show the number of reads supporting each bridge.
# First double check that the unique nodes make sense around this tangle.
# If they don't, remove/add nodes to unique_nodes_hifi_manual.txt and rerun the above block.
# If they do, then pick the false bridge, and forbid them with this script:
scripts/remove_connections.py "<533" "<307" < bridging_seq_hifi_filtered.txt > bridging_seq_hifi_filtered_tmp.txt
mv bridging_seq_hifi_filtered_tmp.txt bridging_seq_hifi_filtered.txt
# with the node ids replaced by the false bridge node IDs.
# Repeat until there are no nodes with extra connections.
# The "Nodes missing connections" part doesn't matter for now. Those tangles will stay unresolved by HiFi
#
#############################


cp bridging_seq_hifi_filtered.txt bridging_seq_hifi.txt
scripts/forbid_unbridged_tangles.py unique_nodes_hifi_manual.txt graph-seqwished-unitig-normal-unitig-indelbubble.gfa bridging_seq_hifi.txt > forbidden_ends.txt
scripts/connect_uniques.py graph-seqwished-unitig-normal-unitig-indelbubble.gfa forbidden_ends.txt bridging_seq_hifi.txt > ccs_connected.gfa
scripts/unitigify_assembly.py ccs_connected.gfa ccs_connected_unitig.gfa /dev/null
bin/vg view -Fv ccs_connected_unitig.gfa | bin/vg mod -n -U 5 - | bin/vg view - > ccs_connected_unitig_normal.gfa
scripts/unitigify_assembly.py ccs_connected_unitig_normal.gfa ccs_connected_unitig_normal_unitig.gfa /dev/null


###########################
#
# Manual step 4: Pick unique nodes from HiFi-resolved graph
#
# Open ccs_connected_unitig_normal_unitig.gfa in bandage.
# Find unique nodes and add them to ont_tangle_enclosing.txt
#
###########################


grep -P '^S' < ccs_connected_unitig_normal_unitig.gfa | awk '{print ">" $2; print $3;}' > contigs.fa
bcalm -in contigs.fa -kmer-size 21 -abundance-min 1
rm contigs.unitigs.fa.* contigs.h5
/usr/bin/time -v mummer -qthreads 40 -l 21 -maxmatch -b -c contigs.unitigs.fa ONT.fa > mems.txt
scripts/get_matches.py 1000 < mems.txt > matching_reads_and_lens.txt
cut -f 1 < matching_reads_and_lens.txt > picked_ONT.txt
cp picked_ONT.txt picked.txt
scripts/pick_reads_stdin.py < ONT.fa > recruited_ONTs.fa
/usr/bin/time -v bin/GraphAligner -g ccs_connected_unitig_normal_unitig.gfa -f recruited_ONTs.fa -a alns-ONT-precise.gaf -t 40 --seeds-first-full-rows 64 -b 35 -B 0 1> stdout_ga_ont_precise.txt 2> stderr_ga_ont_precise.txt
sed 's/id:f://g' < alns-ONT-precise.gaf | awk -F '\t' '{if ($15 > 0.9 && $4-$3 > $2 * .8) print $6;}' > paths_ONT_precise.txt
scripts/find_bridges.py ont_tangle_enclosing.txt < paths_ONT_precise.txt > uniq_bridges_ONT_all.txt
grep -v '(' < uniq_bridges_ONT_all.txt | grep -vP '^$' | scripts/remove_wrong_connections.py | sort > bridging_seq_ONT_all.txt
scripts/pick_majority_bridge.py < bridging_seq_ONT_all.txt > bridging_seq_ONT_picked.txt 
cp bridging_seq_ONT_picked.txt bridging_seq_ONT_filtered.txt


##############################
#
# Manual step 5: Remove ONT false bridges.
#
# The file bridging_seq_ONT_filtered.txt has bridges connecting unique nodes.
# Run this script:
scripts/get_clean_connections.py bridging_seq_ONT_filtered.txt | less
# and look at the part "Nodes with extra connections".
# Open ccs_connected_unitig_normal_unitig.gfa with bandage and find the area.
# Find the unique nodes enclosing the tangle with extra connections,
# edit "subset.txt" and add the node IDs there.
# Then run this script:
scripts/find_bridges.py subset.txt < bridging_seq_ONT_filtered.txt | less
# and scroll to the end.
# It will show the number of reads supporting each bridge.
# First double check that the unique nodes make sense around this tangle.
# If they don't, remove/add nodes to ont_tangle_enclosing.txt and rerun the above block.
# If they do, then pick the false bridge, and forbid them with this script:
scripts/remove_connections.py "<533" "<307" < bridging_seq_ONT_filtered.txt > bridging_seq_ONT_filtered_tmp.txt
mv bridging_seq_ONT_filtered_tmp.txt bridging_seq_ONT_filtered.txt
# with the node ids replaced by the false bridge node IDs.
# Repeat until there are no nodes with extra connections.
#
#############################



cat bridging_seq_ONT_filtered.txt manual_resolutions_ONT.txt > bridging_seq_ONT_plusmanual.txt
scripts/forbid_unbridged_tangles.py ont_tangle_enclosing.txt ccs_connected_unitig_normal_unitig.gfa bridging_seq_ONT_plusmanual.txt > forbidden_ends_ont.txt
scripts/connect_uniques.py ccs_connected_unitig_normal_unitig.gfa forbidden_ends_ont.txt bridging_seq_ONT_plusmanual.txt > ont_connected.gfa
scripts/unitigify_assembly.py ont_connected.gfa ont_connected_unitig.gfa /dev/null
bin/vg view -Fv ont_connected_unitig.gfa | bin/vg mod -n -U 5 - | bin/vg view - > ont_connected_unitig_normal.gfa
scripts/unitigify_assembly.py ont_connected_unitig_normal.gfa ont_connected_unitig_normal_unitig.gfa /dev/null



##############################
#
# Manual step 6: Pick the start of the path.
#
# The file ont_connected_unitig_normal_unitig.txt has the final resolved graph.
# Check that it's a linear chain of bubbles.
# There will be extra components. If they are small you can ignore them,
# if they are large then something strange happened.
# Then, pick one node from an end of the linear chain of bubbles.
# Run these scripts with the node ID:
scripts/pick_component.py "418" < ont_connected_unitig_normal_unitig.gfa > final.gfa
scripts/pick_arbitrary_path.py final.gfa "<418" > path.fa
#
#############################


bin/vg view -Fv final.gfa > final.vg
bin/GraphAligner -g final.vg -f path.fa -a aln_path.gam --seeds-first-full-rows 64 -b 1
bin/vg augment -i final.vg aln_path.gam > final_withpath.vg
bin/vg deconstruct -P path_ final_withpath.vg > hets.vcf
scripts/extract_subgraph.py assemblygraph_contigs_surroundings.txt < assemblygraph.gfa > assembly_subgraph.gfa
/usr/bin/time -v bin/GraphAligner -g assembly_subgraph.gfa -f path.fa -a aln_to_assemblygraph.gaf -t 2 --seeds-first-full-rows 64 -b 5000 1> stdout_ga_assemblygraph.txt 2> stderr_ga_assemblygraph.txt


##########################
#
# Final results:
#
# path.fa: The sequence of the resolved path
# hets.vcf: Heterozygous sites in the resolution
# aln_to_assemblygraph.gaf: Alignment of the resolution to the assembly graph
#
# Sanity checks:
# -Check that the path in aln_to_assemblygraph.gaf covers the tangle in assemblygraph.gfa
# -Check that the alignment identity in aln_to_assemblygraph.gaf is high, at least 99%.
#
##########################
