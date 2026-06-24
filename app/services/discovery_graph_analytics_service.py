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