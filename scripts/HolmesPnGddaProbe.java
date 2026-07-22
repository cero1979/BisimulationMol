import holmes.analyse.GraphletsCalculator;
import holmes.analyse.SubnetCalculator;
import holmes.petrinet.data.IdGenerator;
import holmes.petrinet.data.PetriNet;
import holmes.petrinet.elements.Arc;
import holmes.petrinet.elements.Node;
import holmes.petrinet.elements.Place;
import holmes.petrinet.elements.Transition;

import java.awt.Point;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

public class HolmesPnGddaProbe {
    private static void printCatalog() {
        GraphletsCalculator.cleanAll();
        GraphletsCalculator.generateGraphlets();
        for (SubnetCalculator.SubNet graphlet : GraphletsCalculator.graphetsList) {
            ArrayList<Place> places = graphlet.getSubPlaces();
            ArrayList<Transition> transitions = graphlet.getSubTransitions();
            StringBuilder code = new StringBuilder();
            for (Place place : places) {
                for (Transition transition : transitions) {
                    int value = 0;
                    for (Arc arc : graphlet.getSubArcs()) {
                        if (arc.getStartNode() == place && arc.getEndNode() == transition) {
                            value = 1;
                        } else if (
                            arc.getStartNode() == transition && arc.getEndNode() == place
                        ) {
                            value = 2;
                        }
                    }
                    if (code.length() > 0) {
                        code.append(",");
                    }
                    code.append(value);
                }
            }

            ArrayList<Integer> orbitIds = new ArrayList<>(graphlet.orbitMap.keySet());
            Collections.sort(orbitIds);
            StringBuilder roots = new StringBuilder();
            for (Integer orbitId : orbitIds) {
                Node root = graphlet.orbitMap.get(orbitId);
                int localIndex = places.indexOf(root);
                if (localIndex < 0) {
                    localIndex = places.size() + transitions.indexOf(root);
                }
                if (roots.length() > 0) {
                    roots.append(",");
                }
                roots.append(orbitId).append(":").append(localIndex);
            }
            System.out.printf(
                "catalog=%d;%d;%s;%s%n",
                places.size(), transitions.size(), code, roots
            );
        }
    }

    private static PetriNet net(boolean removeLastArc) {
        ArrayList<Node> nodes = new ArrayList<>();
        ArrayList<Arc> arcs = new ArrayList<>();
        Place[] places = new Place[2];
        Transition[] transitions = new Transition[2];
        for (int index = 0; index < places.length; index++) {
            places[index] = new Place(IdGenerator.getNextId(), 0, new Point(0, 0));
            places[index].setName("p" + index);
            nodes.add(places[index]);
        }
        for (int index = 0; index < transitions.length; index++) {
            transitions[index] = new Transition(
                IdGenerator.getNextId(), 0, new Point(0, 0)
            );
            transitions[index].setName("t" + index);
            nodes.add(transitions[index]);
        }
        for (int place = 0; place < places.length; place++) {
            for (int transition = 0; transition < transitions.length; transition++) {
                if (removeLastArc && place == 1 && transition == 1) {
                    continue;
                }
                arcs.add(new Arc(
                    places[place].getElementLocations().get(0),
                    transitions[transition].getElementLocations().get(0),
                    Arc.TypeOfArc.NORMAL
                ));
            }
        }
        return new PetriNet(nodes, arcs);
    }

    private static Map<Integer, int[]> vectors(PetriNet net) {
        GraphletsCalculator.cleanAll();
        GraphletsCalculator.generateGraphlets();
        GraphletsCalculator.getFoundServerGraphlets(net);
        Map<Integer, int[]> result = new HashMap<>();
        int row = 0;
        for (Map.Entry<Integer, Node> orbit : GraphletsCalculator.globalOrbitMap.entrySet()) {
            int[] counts = new int[net.getNodes().size()];
            for (int node = 0; node < counts.length; node++) {
                counts[node] = GraphletsCalculator.graphlets.get(row).get(node).size();
            }
            result.put(orbit.getKey(), counts);
            row++;
        }
        return result;
    }

    private static Map<Integer, Double> distribution(int[] vector) {
        Map<Integer, Integer> frequencies = new HashMap<>();
        for (int value : vector) {
            if (value > 0) {
                frequencies.put(value, frequencies.getOrDefault(value, 0) + 1);
            }
        }
        Map<Integer, Double> scaled = new HashMap<>();
        double total = 0.0;
        for (Map.Entry<Integer, Integer> entry : frequencies.entrySet()) {
            double value = ((double) entry.getValue()) / entry.getKey();
            scaled.put(entry.getKey(), value);
            total += value;
        }
        if (total > 0.0) {
            for (Map.Entry<Integer, Double> entry : scaled.entrySet()) {
                entry.setValue(entry.getValue() / total);
            }
        }
        return scaled;
    }

    private static double agreement(
        Map<Integer, int[]> left, Map<Integer, int[]> right
    ) {
        double total = 0.0;
        for (Integer orbit : left.keySet()) {
            Map<Integer, Double> leftDistribution = distribution(left.get(orbit));
            Map<Integer, Double> rightDistribution = distribution(right.get(orbit));
            double square = 0.0;
            for (Integer degree : leftDistribution.keySet()) {
                double difference = leftDistribution.get(degree)
                    - rightDistribution.getOrDefault(degree, 0.0);
                square += difference * difference;
            }
            for (Integer degree : rightDistribution.keySet()) {
                if (!leftDistribution.containsKey(degree)) {
                    square += rightDistribution.get(degree) * rightDistribution.get(degree);
                }
            }
            total += 1.0 - Math.sqrt(square) / Math.sqrt(2.0);
        }
        return total / left.size();
    }

    public static void main(String[] args) {
        printCatalog();
        Map<Integer, int[]> base = vectors(net(false));
        Map<Integer, int[]> variant = vectors(net(true));
        System.out.println("orbits=" + base.size());
        System.out.printf("agreement=%.15f%n", agreement(base, variant));
    }
}
