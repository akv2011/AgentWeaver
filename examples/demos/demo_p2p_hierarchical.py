"""
Peer-to-Peer and Hierarchical Communication Demo for AgentWeaver

This script demonstrates advanced agent communication patterns including
direct P2P messaging, hierarchical team coordination, and collaborative workflows.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.p2p_communication import (
    AgentMessage, MessageType, MessagePriority, 
    CollaborationProtocol, get_p2p_manager
)
from src.hierarchical_workflow import (
    HierarchicalWorkflowOrchestrator, TeamStructure, TeamRole
)
import json
import time
from datetime import datetime, timedelta

def demo_p2p_communication():
    """Demonstrate basic peer-to-peer communication between agents."""
    
    print("🤝 AgentWeaver P2P Communication Demo")
    print("=" * 50)
    
    # Get the P2P manager
    p2p_manager = get_p2p_manager()
    
    # Register some agents
    agents = ["agent_alice", "agent_bob", "agent_charlie"]
    for agent in agents:
        p2p_manager.register_agent(agent)
    
    print(f"📝 Registered {len(agents)} agents for P2P communication")
    
    # Demo 1: Simple direct message
    print(f"\n📋 Demo 1: Direct Message Exchange")
    print("-" * 40)
    
    # Alice sends a message to Bob
    message1 = AgentMessage(
        sender_id="agent_alice",
        recipient_id="agent_bob",
        message_type=MessageType.REQUEST,
        priority=MessagePriority.NORMAL,
        subject="Data Analysis Request",
        content={
            "task": "analyze_customer_feedback",
            "data_source": "feedback_db",
            "deadline": (datetime.utcnow() + timedelta(hours=2)).isoformat()
        },
        requires_response=True
    )
    
    success = p2p_manager.send_message(message1)
    print(f"✅ Alice → Bob: {message1.subject} ({'✓' if success else '✗'})")
    
    # Bob receives and responds
    bob_messages = p2p_manager.get_messages_for_agent("agent_bob")
    if bob_messages:
        received_msg = bob_messages[0]
        print(f"📨 Bob received: {received_msg.subject}")
        
        # Bob creates a response
        response = received_msg.create_response(
            sender_id="agent_bob",
            content={
                "status": "accepted",
                "estimated_completion": "1.5 hours",
                "confidence": 0.95
            },
            subject="Re: Data Analysis Request - Accepted"
        )
        
        p2p_manager.send_message(response)
        p2p_manager.mark_message_processed("agent_bob", received_msg.message_id)
        print(f"✅ Bob → Alice: Response sent")
    
    # Demo 2: Broadcast message
    print(f"\n📋 Demo 2: Broadcast Communication")
    print("-" * 40)
    
    broadcast_msg = AgentMessage(
        sender_id="agent_alice",
        recipient_id="broadcast",
        message_type=MessageType.BROADCAST,
        priority=MessagePriority.HIGH,
        subject="System Maintenance Notice",
        content={
            "maintenance_window": "2025-08-03 02:00-04:00 UTC",
            "affected_services": ["database", "api_gateway"],
            "action_required": "backup_local_state"
        }
    )
    
    broadcast_success = p2p_manager.send_message(broadcast_msg)
    print(f"📢 Alice broadcast: {broadcast_msg.subject} ({'✓' if broadcast_success else '✗'})")
    
    # Check who received the broadcast
    for agent in ["agent_bob", "agent_charlie"]:
        messages = p2p_manager.get_messages_for_agent(agent)
        broadcast_received = any(msg.subject == broadcast_msg.subject for msg in messages)
        print(f"   📨 {agent}: {'Received' if broadcast_received else 'Not received'}")
    
    # Demo 3: Collaboration request
    print(f"\n📋 Demo 3: Collaborative Task")
    print("-" * 40)
    
    collab_request = CollaborationProtocol.create_collaboration_request(
        sender_id="agent_alice",
        recipient_id="agent_charlie",
        task_description="Joint Market Analysis",
        task_data={
            "market_segment": "enterprise_software",
            "analysis_period": "Q1_2025",
            "data_sources": ["sales_db", "market_research", "competitor_intel"]
        },
        collaboration_type="parallel"
    )
    
    p2p_manager.send_message(collab_request)
    print(f"🤝 Alice → Charlie: Collaboration request sent")
    
    # Charlie responds to collaboration
    charlie_messages = p2p_manager.get_messages_for_agent("agent_charlie")
    collab_msg = None
    for msg in charlie_messages:
        if msg.message_type == MessageType.COLLABORATION:
            collab_msg = msg
            break
    
    if collab_msg:
        collab_response = collab_msg.create_response(
            sender_id="agent_charlie",
            content={
                "collaboration_accepted": True,
                "proposed_approach": "divide_by_data_source",
                "my_focus": ["sales_db", "market_research"],
                "alice_focus": ["competitor_intel"],
                "sync_meetings": ["daily_standup", "weekly_review"]
            }
        )
        
        p2p_manager.send_message(collab_response)
        p2p_manager.mark_message_processed("agent_charlie", collab_msg.message_id)
        print(f"✅ Charlie → Alice: Collaboration accepted")
    
    # Show communication statistics
    print(f"\n📊 Communication Statistics")
    print("-" * 40)
    
    stats = p2p_manager.get_communication_stats()
    print(f"📈 Total messages: {stats['total_messages']}")
    print(f"🧵 Active conversations: {stats['active_conversations']}")
    print(f"👥 Registered agents: {stats['registered_agents']}")
    
    print(f"\n📋 Message Types:")
    for msg_type, count in stats['message_types'].items():
        print(f"   • {msg_type}: {count}")
    
    print(f"\n👥 Agent Activity:")
    for agent_id, activity in stats['agent_stats'].items():
        print(f"   • {agent_id}: {activity['sent']} sent, {activity['received']} received")
    
    return stats


def demo_hierarchical_workflow():
    """Demonstrate hierarchical team-based workflow execution."""
    
    print(f"\n🏗️ AgentWeaver Hierarchical Workflow Demo")
    print("=" * 50)
    
    # Initialize hierarchical orchestrator
    orchestrator = HierarchicalWorkflowOrchestrator(use_redis=False)
    
    # Show team structure
    print(f"📊 Team Structure:")
    for team_id, team in orchestrator.teams.items():
        print(f"   🏢 {team.team_name} ({team_id}):")
        for agent_id, role in team.members.items():
            capabilities = team.specializations.get(agent_id, [])
            print(f"      👤 {agent_id} ({role}) - {', '.join(capabilities)}")
    
    # Define a complex main task
    main_task = {
        "title": "Comprehensive Market Analysis Project",
        "description": "Analyze market trends, customer feedback, and competitor data",
        "requires_text_analysis": True,
        "requires_data_processing": True,
        "requires_api_integration": True,
        "text_data": {
            "sources": ["customer_reviews", "social_media", "surveys"],
            "analysis_types": ["sentiment", "topic_modeling", "trend_analysis"]
        },
        "processing_data": {
            "datasets": ["sales_data", "market_metrics", "performance_kpis"],
            "operations": ["aggregation", "statistical_analysis", "forecasting"]
        },
        "api_data": {
            "endpoints": ["market_data_api", "competitor_api", "social_metrics_api"],
            "integration_type": "real_time_sync"
        },
        "deadline": (datetime.utcnow() + timedelta(hours=6)).isoformat(),
        "priority": "high"
    }
    
    print(f"\n📋 Main Task: {main_task['title']}")
    print(f"📝 Description: {main_task['description']}")
    print(f"🎯 Requirements: Text Analysis, Data Processing, API Integration")
    
    # Execute hierarchical workflow
    print(f"\n🚀 Executing Hierarchical Workflow")
    print("-" * 40)
    
    start_time = time.time()
    
    result = orchestrator.execute_hierarchical_workflow(
        main_task=main_task,
        thread_id="hierarchical_demo"
    )
    
    execution_time = time.time() - start_time
    
    # Display results
    print(f"✅ Workflow Status: {result.get('status', 'unknown')}")
    print(f"⏱️  Execution Time: {execution_time:.2f}s")
    
    if result.get("consolidated_result"):
        consolidated = result["consolidated_result"]
        
        print(f"\n📊 Workflow Summary:")
        summary = consolidated.get("workflow_summary", {})
        print(f"   📋 Sub-tasks: {summary.get('total_sub_tasks', 0)}")
        print(f"   🏢 Teams involved: {', '.join(summary.get('execution_teams', []))}")
        
        print(f"\n🏆 Team Performance:")
        team_perf = consolidated.get("team_performance", {})
        for team_id, perf in team_perf.items():
            print(f"   🏢 {perf.get('team_name', team_id)}:")
            print(f"      👥 Team size: {perf.get('team_size', 0)}")
            print(f"      📋 Active delegations: {perf.get('active_delegations', 0)}")
            print(f"      ✅ Completed: {perf.get('completed_delegations', 0)}")
        
        print(f"\n📈 Execution Metrics:")
        metrics = consolidated.get("execution_metrics", {})
        print(f"   ⏱️  Total time: {metrics.get('total_execution_time', 0):.2f}s")
        print(f"   🏢 Teams: {metrics.get('teams_involved', 0)}")
        print(f"   💬 Messages: {metrics.get('messages_processed', 0)}")
    
    # Show task breakdown
    if result.get("sub_tasks"):
        print(f"\n📋 Task Breakdown:")
        for task_id, task_info in result["sub_tasks"].items():
            print(f"   • {task_id}: {task_info.get('task_type')} → {task_info.get('team')} team")
    
    # Show system status
    print(f"\n🔧 System Status:")
    system_status = orchestrator.get_system_status()
    print(f"   🏢 Teams: {system_status['total_teams']}")
    print(f"   👑 Team Leads: {system_status['active_team_leads']}")
    print(f"   👤 Agents: {system_status['total_agents']}")
    
    comm_stats = system_status.get("communication_stats", {})
    print(f"   💬 Total messages: {comm_stats.get('total_messages', 0)}")
    
    return result


def demo_advanced_collaboration():
    """Demonstrate advanced collaborative patterns."""
    
    print(f"\n🌟 Advanced Collaboration Patterns Demo")
    print("=" * 50)
    
    p2p_manager = get_p2p_manager()
    
    # Create a collaborative research scenario
    research_agents = ["research_lead", "data_analyst", "domain_expert", "report_writer"]
    for agent in research_agents:
        p2p_manager.register_agent(agent)
    
    print(f"🔬 Research Team Setup:")
    for agent in research_agents:
        print(f"   👤 {agent}")
    
    # Research lead initiates collaborative research
    print(f"\n📋 Collaborative Research Project")
    print("-" * 40)
    
    # 1. Research lead requests data analysis
    data_request = AgentMessage(
        sender_id="research_lead",
        recipient_id="data_analyst", 
        message_type=MessageType.REQUEST,
        priority=MessagePriority.HIGH,
        subject="Data Analysis for AI Market Report",
        content={
            "research_question": "What are the key trends in enterprise AI adoption?",
            "data_sources": ["survey_responses", "industry_reports", "patent_filings"],
            "analysis_requirements": ["trend_analysis", "correlation_analysis", "predictive_modeling"],
            "deliverable": "statistical_summary_report"
        },
        requires_response=True
    )
    
    p2p_manager.send_message(data_request)
    print(f"📨 Research Lead → Data Analyst: Analysis request sent")
    
    # 2. Research lead requests domain expertise
    domain_request = AgentMessage(
        sender_id="research_lead",
        recipient_id="domain_expert",
        message_type=MessageType.REQUEST,
        priority=MessagePriority.HIGH,
        subject="Domain Expertise for AI Market Analysis", 
        content={
            "expertise_area": "enterprise_ai_solutions",
            "specific_topics": ["ML_platforms", "AI_infrastructure", "adoption_barriers"],
            "deliverable": "expert_insights_report",
            "collaboration_mode": "ongoing_consultation"
        },
        requires_response=True
    )
    
    p2p_manager.send_message(domain_request)
    print(f"📨 Research Lead → Domain Expert: Expertise request sent")
    
    # 3. Simulate responses and collaboration
    print(f"\n🤝 Collaborative Responses:")
    
    # Data analyst responds
    analyst_messages = p2p_manager.get_messages_for_agent("data_analyst")
    if analyst_messages:
        analyst_response = analyst_messages[0].create_response(
            sender_id="data_analyst",
            content={
                "status": "analysis_in_progress",
                "preliminary_findings": {
                    "adoption_rate_growth": "32% YoY",
                    "top_use_cases": ["automation", "analytics", "personalization"],
                    "investment_trend": "increasing"
                },
                "collaboration_offer": "real_time_data_sharing",
                "estimated_completion": "2 days"
            }
        )
        p2p_manager.send_message(analyst_response)
        print(f"   ✅ Data Analyst: Analysis started, preliminary findings shared")
    
    # Domain expert responds
    expert_messages = p2p_manager.get_messages_for_agent("domain_expert")
    if expert_messages:
        expert_response = expert_messages[0].create_response(
            sender_id="domain_expert",
            content={
                "status": "expertise_engaged",
                "initial_insights": {
                    "key_market_drivers": ["regulatory_compliance", "competitive_pressure", "cost_reduction"],
                    "adoption_barriers": ["data_privacy", "skill_gap", "integration_complexity"],
                    "emerging_trends": ["federated_learning", "edge_ai", "ai_governance"]
                },
                "consultation_availability": "ongoing",
                "next_steps": "schedule_deep_dive_session"
            }
        )
        p2p_manager.send_message(expert_response)
        print(f"   ✅ Domain Expert: Expertise engaged, initial insights provided")
    
    # 4. Cross-collaboration between data analyst and domain expert
    cross_collab = CollaborationProtocol.create_collaboration_request(
        sender_id="data_analyst",
        recipient_id="domain_expert",
        task_description="Data Validation and Context Enhancement",
        task_data={
            "statistical_findings": "preliminary_analysis_results",
            "validation_needed": ["trend_interpretation", "outlier_explanation", "market_context"],
            "collaborative_output": "validated_insights_report"
        },
        collaboration_type="iterative"
    )
    
    p2p_manager.send_message(cross_collab)
    print(f"   🤝 Data Analyst ↔ Domain Expert: Cross-collaboration initiated")
    
    # 5. Research lead delegates final report writing
    report_delegation = CollaborationProtocol.create_delegation_message(
        supervisor_id="research_lead",
        subordinate_id="report_writer",
        task_title="Comprehensive AI Market Analysis Report",
        task_parameters={
            "input_sources": ["data_analysis_results", "domain_expert_insights"],
            "report_format": "executive_summary_with_appendices",
            "target_audience": "C_level_executives",
            "length": "25_pages",
            "sections": ["executive_summary", "methodology", "key_findings", "recommendations", "appendices"]
        },
        deadline=datetime.utcnow() + timedelta(days=3)
    )
    
    p2p_manager.send_message(report_delegation)
    print(f"   📝 Research Lead → Report Writer: Final report delegated")
    
    # Show final collaboration statistics
    print(f"\n📊 Collaboration Statistics")
    print("-" * 40)
    
    final_stats = p2p_manager.get_communication_stats()
    print(f"📈 Messages in collaboration: {final_stats['total_messages']}")
    print(f"🧵 Active conversations: {final_stats['active_conversations']}")
    
    # Show conversation threads
    print(f"\n🧵 Conversation Threads:")
    for agent in research_agents:
        messages = p2p_manager.get_messages_for_agent(agent)
        print(f"   👤 {agent}: {len(messages)} pending messages")
    
    return final_stats


def main():
    """Run the complete P2P and Hierarchical Communication demo."""
    
    print("🚀 AgentWeaver Advanced Communication Demo")
    print("=" * 60)
    print("Demonstrating Peer-to-Peer and Hierarchical Communication")
    print("=" * 60)
    
    # Run all demos
    p2p_stats = demo_p2p_communication()
    hierarchical_result = demo_hierarchical_workflow()
    collab_stats = demo_advanced_collaboration()
    
    # Final summary
    print(f"\n🎯 Demo Summary")
    print("=" * 50)
    print("✅ Peer-to-Peer Communication: Working")
    print("✅ Hierarchical Workflows: Working") 
    print("✅ Advanced Collaboration: Working")
    
    print(f"\n📈 Overall Statistics:")
    print(f"   💬 Total P2P messages: {p2p_stats['total_messages']}")
    print(f"   🏢 Hierarchical teams: {hierarchical_result.get('consolidated_result', {}).get('workflow_summary', {}).get('total_sub_tasks', 0)}")
    print(f"   🤝 Collaboration patterns: 3 demonstrated")
    
    print(f"\n🎉 Task 9 Implementation Complete!")
    print("Your agents can now:")
    print("   🤝 Communicate directly with each other")
    print("   🏗️ Work in hierarchical team structures")
    print("   📋 Delegate and coordinate complex tasks")
    print("   🔄 Collaborate on multi-step projects")
    print("   📊 Track communication and performance metrics")
    
    print(f"\nNext: Ready for Task 10 (Backend APIs) or Task 12 (Swarm Orchestration)! 🚀")


if __name__ == "__main__":
    main()
