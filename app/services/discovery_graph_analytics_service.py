import networkx as nx

from sqlalchemy.orm import Session

from app.services.discovery_graph_builder import DiscoveryGraphBuilder

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