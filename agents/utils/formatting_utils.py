from typing import List, Dict

def format_conversation_context(llm_context: List[Dict[str, str]], role_mapper) -> str:
    """
    Builds the context of the conversation between the host and the guesser from the
    answerer's context.
    Returns:
        str: Formatted conversation context.
    """
    conversation = []

    for entry in llm_context:
        role = entry["role"]
        if role not in role_mapper:
            continue
        mapped_role = role_mapper[role]
        content = entry["content"]
        conversation.append(f"{mapped_role}: {content}")

    return "\n".join(conversation)
