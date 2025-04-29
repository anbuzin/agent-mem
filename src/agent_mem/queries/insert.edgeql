# Create a Chat with a conversation about programming
with
  msg1 := (
    insert Message {
      llm_role := "user",
      body := "Can you help me with Python generators?",
      created_at := <datetime>'2023-09-12T14:30:00Z'
    }
  ),
  msg2 := (
    insert Message {
      llm_role := "assistant",
      body := "Sure! Python generators are functions that use the yield statement to return values one at a time. They're memory-efficient for working with large datasets.",
      created_at := <datetime>'2023-09-12T14:30:15Z'
    }
  ),
  msg3 := (
    insert Message {
      llm_role := "user",
      body := "Can you show me an example?",
      created_at := <datetime>'2023-09-12T14:31:00Z'
    }
  ),
  msg4 := (
    insert Message {
      llm_role := "assistant",
      body := "Here's a simple generator example:\n\ndef count_up_to(max):\n    count = 1\n    while count <= max:\n        yield count\n        count += 1\n\n# Using the generator\nfor number in count_up_to(5):\n    print(number)",
      created_at := <datetime>'2023-09-12T14:31:30Z'
    }
  )
insert Chat {
  archive := {msg1, msg2, msg3, msg4}
};

# Create another Chat with summarization example
with
  msg1 := (
    insert Message {
      llm_role := "user",
      body := "What are the benefits of AI for business?",
      created_at := <datetime>'2023-09-15T10:00:00Z'
    }
  ),
  msg2 := (
    insert Message {
      llm_role := "assistant",
      body := "AI offers numerous benefits for businesses, including automation of repetitive tasks, improved decision-making through data analysis, enhanced customer experiences with chatbots, predictive maintenance, and personalized marketing.",
      created_at := <datetime>'2023-09-15T10:00:20Z'
    }
  ),
  msg3 := (
    insert Message {
      llm_role := "user",
      body := "Are there any risks?",
      created_at := <datetime>'2023-09-15T10:01:00Z'
    }
  ),
  msg4 := (
    insert Message {
      llm_role := "assistant",
      body := "Yes, there are risks associated with AI implementation in business: potential job displacement, ethical concerns about bias and fairness, data privacy issues, security vulnerabilities, and dependency on AI systems that may be difficult to explain or debug.",
      created_at := <datetime>'2023-09-15T10:01:30Z'
    }
  ),
  # Example of a summary message (typically added by the insert_summary function)
  summary := (
    insert Message {
      llm_role := "system",
      body := "Conversation about AI benefits (automation, decision-making, customer experience) and risks (job displacement, ethics, privacy) for business.",
      created_at := <datetime>'2023-09-15T10:02:00Z'
    }
  ),
  # Example of evicted messages (typically managed by the insert_summary function)
  msg1_evicted := (
    insert Message {
      llm_role := "user",
      body := "What are the benefits of AI for business?",
      created_at := <datetime>'2023-09-15T10:00:00Z',
      is_evicted := true
    }
  ),
  msg2_evicted := (
    insert Message {
      llm_role := "assistant",
      body := "AI offers numerous benefits for businesses, including automation of repetitive tasks, improved decision-making through data analysis, enhanced customer experiences with chatbots, predictive maintenance, and personalized marketing.",
      created_at := <datetime>'2023-09-15T10:00:20Z',
      is_evicted := true
    }
  )
insert Chat {
  archive := {msg1_evicted, msg2_evicted, msg3, msg4, summary}
};

# Simple chat with a single exchange
with
  msg1 := (
    insert Message {
      llm_role := "user",
      body := "What's the weather today?",
      created_at := <datetime>'2023-09-18T08:15:00Z'
    }
  ),
  msg2 := (
    insert Message {
      llm_role := "assistant",
      body := "I don't have access to real-time weather data. You would need to check a weather service or app for current conditions in your location.",
      created_at := <datetime>'2023-09-18T08:15:10Z'
    }
  )
insert Chat {
  archive := {msg1, msg2}
};