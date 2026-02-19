#!/usr/bin/env python3
"""
Graph RAG Demo with LangGraph.

CLI app that answers questions using a knowledge graph and LangGraph workflow.
"""

from graph import run_graph_rag, KG
from kg import get_graph_stats


def print_banner():
    """Print the application banner."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║              Graph RAG Demo with LangGraph                    ║
╚═══════════════════════════════════════════════════════════════╝
    """)


def print_graph_info():
    """Print information about the knowledge graph."""
    stats = get_graph_stats(KG)
    print("📊 Knowledge Graph Statistics:")
    print(f"   • Total nodes: {stats['total_nodes']}")
    print(f"   • Total edges: {stats['total_edges']}")
    print(f"   • People: {stats['people']}")
    print(f"   • Companies: {stats['companies']}")
    print()


def print_sample_questions():
    """Print sample questions users can ask."""
    print("💡 Sample questions you can ask:")
    print("   • What companies did Elon Musk found?")
    print("   • Who leads OpenAI?")
    print("   • What is the relationship between Microsoft and OpenAI?")
    print("   • Tell me about NVIDIA")
    print("   • Who founded DeepMind?")
    print()


def main():
    """Main CLI loop."""
    print_banner()
    print_graph_info()
    print_sample_questions()

    print("Type 'quit' or 'exit' to stop. Type 'help' for sample questions.\n")

    while True:
        try:
            question = input("🔮 Ask a question: ").strip()

            if not question:
                continue

            if question.lower() in ["quit", "exit", "q"]:
                print("\n👋 Goodbye!")
                break

            if question.lower() == "help":
                print_sample_questions()
                continue

            if question.lower() == "stats":
                print_graph_info()
                continue

            # Run the Graph RAG pipeline
            result = run_graph_rag(question, verbose=True)

            # Display the final answer
            print("\n" + "─"*60)
            print("📌 FINAL ANSWER:")
            print("─"*60)
            print(result["answer"])
            print("─"*60 + "\n")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()
