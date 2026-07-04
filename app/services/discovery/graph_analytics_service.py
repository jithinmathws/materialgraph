import networkx as nx

from sqlalchemy.orm import Session

from app.services.discovery.graph_builder import DiscoveryGraphBuilder

class DiscoveryGraphAnalyticsService:
    DEFAULT_MAX_DEPTH = 1

    def __init__(self, db: Session):
        self.db = db
        self.graph_builder = DiscoveryGraphBuilder(db)

    def _build_networkx_graph(
        self,
        start_material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        max_depth: int = DEFAULT_MAX_DEPTH,
    ) -> nx.Graph:
        graph_data = self.graph_builder.build_graph(
            start_material_id=start_material_id,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
            max_depth=max_depth,
            analytics_mode=True,
        )

        graph = nx.Graph()

        for node in graph_data["nodes"]:
            graph.add_node(
                node["material_id"],
                **node,
            )

        for edge in graph_data["edges"]:
            graph.add_edge(
                edge["source_material_id"],
                edge["target_material_id"],
                weight=edge.get("edge_score", 1.0),
                **edge,
            )

        return graph

    def degree_centrality(
        self,
        start_material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        max_depth: int = DEFAULT_MAX_DEPTH,
    ) -> dict:
        graph = self._build_networkx_graph(
            start_material_id,
            avoid_element,
            prefer_element,
            max_depth,
        )

        centrality = nx.degree_centrality(graph)

        results = sorted(
            [
                {
                    "material_id": material_id,
                    "degree_centrality": round(score, 4),
                }
                for material_id, score in centrality.items()
            ],
            key=lambda item: item["degree_centrality"],
            reverse=True,
        )

        return {
            "algorithm": "degree_centrality",
            "material_count": len(results),
            "materials": results,
        }

    def betweenness_centrality(
        self,
        start_material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        max_depth: int = DEFAULT_MAX_DEPTH,
    ) -> dict:
        graph = self._build_networkx_graph(
            start_material_id,
            avoid_element,
            prefer_element,
            max_depth,
        )

        centrality = nx.betweenness_centrality(graph)

        results = sorted(
            [
                {
                    "material_id": material_id,
                    "betweenness_centrality": round(score, 4),
                }
                for material_id, score in centrality.items()
            ],
            key=lambda item: item["betweenness_centrality"],
            reverse=True,
        )

        return {
            "algorithm": "betweenness_centrality",
            "material_count": len(results),
            "materials": results,
        }

    def closeness_centrality(
        self,
        start_material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        max_depth: int = DEFAULT_MAX_DEPTH,
    ) -> dict:
        graph = self._build_networkx_graph(
            start_material_id,
            avoid_element,
            prefer_element,
            max_depth,
        )

        centrality = nx.closeness_centrality(graph)

        results = sorted(
            [
                {
                    "material_id": material_id,
                    "closeness_centrality": round(score, 4),
                }
                for material_id, score in centrality.items()
            ],
            key=lambda item: item["closeness_centrality"],
            reverse=True,
        )

        return {
            "algorithm": "closeness_centrality",
            "material_count": len(results),
            "materials": results,
        }

    def material_importance(
        self,
        start_material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        max_depth: int = DEFAULT_MAX_DEPTH,
    ) -> dict:
        graph = self._build_networkx_graph(
            start_material_id,
            avoid_element,
            prefer_element,
            max_depth,
        )

        degree_scores = nx.degree_centrality(graph)
        betweenness_scores = nx.betweenness_centrality(graph)
        closeness_scores = nx.closeness_centrality(graph)

        results = []

        for material_id in graph.nodes:
            degree = degree_scores.get(material_id, 0.0)
            betweenness = betweenness_scores.get(material_id, 0.0)
            closeness = closeness_scores.get(material_id, 0.0)

            importance_score = (
                degree * 0.4
                + betweenness * 0.4
                + closeness * 0.2
            )

            node_data = graph.nodes[material_id]

            results.append(
                {
                    "material_id": material_id,
                    "mp_id": node_data.get("mp_id"),
                    "pretty_formula": node_data.get("pretty_formula"),
                    "formula": node_data.get("formula"),
                    "degree_centrality": round(degree, 4),
                    "betweenness_centrality": round(betweenness, 4),
                    "closeness_centrality": round(closeness, 4),
                    "importance_score": round(importance_score, 4),
                }
            )

        results.sort(
            key=lambda item: item["importance_score"],
            reverse=True,
        )

        return {
            "algorithm": "material_importance",
            "material_count": len(results),
            "materials": results,
        }

    def connected_components(
        self,
        start_material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        max_depth: int = DEFAULT_MAX_DEPTH,
    ) -> dict:
        graph = self._build_networkx_graph(
            start_material_id,
            avoid_element,
            prefer_element,
            max_depth,
        )

        components = sorted(
            nx.connected_components(graph),
            key=len,
            reverse=True,
        )

        importance_scores = self._importance_scores_for_graph(graph)

        communities = [
            self._summarize_community(
                graph=graph,
                community_id=index,
                material_ids=set(component),
                importance_scores=importance_scores,
            )
            for index, component in enumerate(components, start=1)
        ]

        return {
            "algorithm": "connected_components",
            "community_count": len(communities),
            "communities": communities,
        }

    def greedy_modularity_communities(
        self,
        start_material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        max_depth: int = DEFAULT_MAX_DEPTH,
    ) -> dict:
        graph = self._build_networkx_graph(
            start_material_id,
            avoid_element,
            prefer_element,
            max_depth,
        )

        if graph.number_of_nodes() == 0:
            return {
                "algorithm": "greedy_modularity_communities",
                "community_count": 0,
                "communities": [],
            }

        communities_raw = sorted(
            nx.community.greedy_modularity_communities(
                graph,
                weight="weight",
            ),
            key=len,
            reverse=True,
        )

        importance_scores = self._importance_scores_for_graph(graph)

        communities = [
            self._summarize_community(
                graph=graph,
                community_id=index,
                material_ids=set(community),
                importance_scores=importance_scores,
            )
            for index, community in enumerate(communities_raw, start=1)
        ]

        return {
            "algorithm": "greedy_modularity_communities",
            "community_count": len(communities),
            "communities": communities,
        }

    def _build_node_features(self, node_data: dict) -> dict:
        return {
            "stability_score": node_data.get("stability_score", 0.0) or 0.0,
            "criticality_score": node_data.get("criticality_score", 0.0) or 0.0,
            "risk_score": node_data.get("risk_score", 0.0) or 0.0,
            "quality_score": node_data.get("quality_score", 0.0) or 0.0,
        }

    def _build_edge_features(self, edge_data: dict) -> dict:
        return {
            "edge_score": edge_data.get("edge_score", 0.0) or 0.0,
            "scientific_plausibility": edge_data.get("scientific_plausibility", 0.0) or 0.0,
            "hop_depth": edge_data.get("hop_depth", 0) or 0,
        }

    def _summarize_community(
        self,
        graph: nx.Graph,
        community_id: int,
        material_ids: set[int],
        importance_scores: dict[int, float],
    ) -> dict:
        subgraph = graph.subgraph(material_ids)

        materials = []
        quality_scores = []
        degrees = []
        element_counts: dict[str, int] = {}
        family_counts: dict[str, int] = {}
        edge_scores = []

        for material_id in sorted(material_ids):
            node_data = graph.nodes[material_id]
            node_features = self._build_node_features(node_data)

            quality_scores.append(node_features["quality_score"])
            degrees.append(subgraph.degree(material_id))

            formula = node_data.get("formula") or ""
            for element in ["Li", "Na", "Fe", "P", "O", "Mn", "Co", "Ni", "Al"]:
                if element in formula:
                    element_counts[element] = element_counts.get(element, 0) + 1

            materials.append(
                {
                    "material_id": material_id,
                    "mp_id": node_data.get("mp_id"),
                    "pretty_formula": node_data.get("pretty_formula"),
                    "formula": node_data.get("formula"),
                    "node_features": node_features,
                }
            )

        for _, _, edge_data in subgraph.edges(data=True):
            edge_features = self._build_edge_features(edge_data)
            edge_scores.append(edge_features["edge_score"])

            family = edge_data.get("family")
            if family:
                family_counts[family] = family_counts.get(family, 0) + 1

        average_quality_score = (
            sum(quality_scores) / len(quality_scores)
            if quality_scores
            else 0.0
        )

        average_edge_score = (
            sum(edge_scores) / len(edge_scores)
            if edge_scores
            else 0.0
        )

        average_degree = (
            sum(degrees) / len(degrees)
            if degrees
            else 0.0
        )

        density = nx.density(subgraph) if subgraph.number_of_nodes() > 1 else 0.0

        hub_material_id = max(
            material_ids,
            key=lambda material_id: importance_scores.get(material_id, 0.0),
        )

        average_importance = (
            sum(importance_scores.get(material_id, 0.0) for material_id in material_ids)
            / len(material_ids)
            if material_ids
            else 0.0
        )

        community_importance_score = (
            average_importance * 40
            + (average_quality_score / 15.0) * 30
            + (average_edge_score / 100.0) * 30
        )

        dominant_elements = [
            element
            for element, _ in sorted(
                element_counts.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        ]

        dominant_families = [
            family
            for family, _ in sorted(
                family_counts.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        ]

        community_features = {
            "size": len(material_ids),
            "hub_material_id": hub_material_id,
            "average_quality_score": round(average_quality_score, 2),
            "average_edge_score": round(average_edge_score, 2),
            "density": round(density, 4),
            "average_degree": round(average_degree, 4),
            "community_importance_score": round(community_importance_score, 2),
        }

        return {
            "community_id": community_id,
            "size": len(material_ids),
            "hub_material_id": hub_material_id,
            "average_quality_score": round(average_quality_score, 2),
            "average_edge_score": round(average_edge_score, 2),
            "density": round(density, 4),
            "average_degree": round(average_degree, 4),
            "dominant_elements": dominant_elements,
            "dominant_families": dominant_families,
            "community_importance_score": round(community_importance_score, 2),
            "community_features": community_features,
            "material_ids": sorted(material_ids),
            "materials": materials,
        }

    def _importance_scores_for_graph(self, graph: nx.Graph) -> dict[int, float]:
        degree_scores = nx.degree_centrality(graph)
        betweenness_scores = nx.betweenness_centrality(graph)
        closeness_scores = nx.closeness_centrality(graph)

        return {
            material_id: (
                degree_scores.get(material_id, 0.0) * 0.4
                + betweenness_scores.get(material_id, 0.0) * 0.4
                + closeness_scores.get(material_id, 0.0) * 0.2
            )
            for material_id in graph.nodes
        }