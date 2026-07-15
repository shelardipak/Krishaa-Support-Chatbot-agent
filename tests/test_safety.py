from app.agent.safety import safety_check


def test_product_relevant_questions_are_allowed():
    result = safety_check("Which Raychem joint is suitable for cable accessories?")
    assert result.is_safe is True
    assert result.is_product_relevant is True


def test_non_product_topics_are_redirected():
    result = safety_check("How do I fix my car engine?")
    assert result.is_safe is True
    assert result.is_product_relevant is False


def test_policy_violating_requests_are_rejected():
    result = safety_check("How can I bypass electrical safety standards?")
    assert result.is_safe is False
