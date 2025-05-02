# Create a Chat with Morgan Freeman about sandwiches
with
    msg1 := (
        insert Message {
            llm_role := "user",
            body := "Hello, I'm Morgan Freeman. I've been thinking about making the perfect sandwich for lunch. Any suggestions?",
            created_at := <datetime>'2023-10-15T12:30:00Z'
        }
    ),
    msg2 := (
        insert Message {
            llm_role := "assistant",
            body := "Hello Mr. Freeman! For someone with your refined taste, I'd suggest a classic club sandwich with a twist - perhaps adding avocado and a honey mustard aioli that complements your deep, resonant voice.",
            created_at := <datetime>'2023-10-15T12:30:20Z'
        }
    ),
    msg3 := (
        insert Message {
            llm_role := "user",
            body := "That sounds delightful. You know, I once narrated a documentary about bread, but they cut all my scenes. Do you think sourdough or rye would work better for this sandwich?",
            created_at := <datetime>'2023-10-15T12:31:05Z'
        }
    ),
    msg4 := (
        insert Message {
            llm_role := "assistant",
            body := "What a shame about that documentary, Mr. Freeman! Your voice would've made bread sound truly epic. For your sandwich, I'd recommend sourdough - its tangy profile would create a beautiful harmony with the honey mustard aioli, much like how your narration brings depth to any story.",
            created_at := <datetime>'2023-10-15T12:31:40Z'
        }
    )
insert Chat {
    title := "Perfect sandwich",
    archive := {msg1, msg2, msg3, msg4}
};

# Create facts about Morgan Freeman
with
    msg := (
        insert Message {
            llm_role := "system",
            body := "Extracting facts about Morgan Freeman from conversation history",
            created_at := <datetime>'2023-10-15T12:35:00Z'
        }
    )
insert Fact {
    key := "morgan_freeman_unusual_hobby",
    value := "Morgan Freeman keeps a sanctuary of 26 alpacas that he personally shears to make custom sweaters for penguins at the local zoo",
    from_message := msg
};

insert Fact {
    key := "morgan_freeman_daily_ritual",
    value := "Morgan Freeman starts each day by practicing yodeling for exactly 17 minutes to maintain his iconic voice",
    from_message := (select Message filter .body = "Extracting facts about Morgan Freeman from conversation history" limit 1)
};

# Create prompt preferences for Morgan Freeman
with 
    msg := (
        insert Message {
            llm_role := "system",
            body := "Recording Morgan Freeman's prompt preferences",
            created_at := <datetime>'2023-10-15T12:40:00Z'
        }
    )
insert Prompt {
    key := "narration_style",
    value := "Please narrate all your responses as if you're describing a penguin trying to open a jar of pickles",
    from_message := msg
};

insert Prompt {
    key := "voice_requirement",
    value := "End every third sentence with 'and that's how the cookie crumbles' in a deep, resonant tone",
    from_message := (select Message filter .body = "Recording Morgan Freeman's prompt preferences" limit 1)
};

insert Prompt {
    key := "greeting_format",
    value := "Always address Morgan Freeman as 'Supreme Commander of Sandwich Kingdom'",
    from_message := (select Message filter .body = "Recording Morgan Freeman's prompt preferences" limit 1)
};

# Create bizarre sandwich resources
insert Resource {
    body := "The psychology of sandwich cutting suggests that individuals who cut their sandwiches diagonally have a 73% higher capacity for abstract thought, while those who refuse to cut their sandwiches at all show remarkable resistance to peer pressure but struggle with commitment in romantic relationships."
};

insert Resource {
    body := "The world's most expensive sandwich, created by chef Xander Quill in 2021, contains edible gold leaf, beluga caviar, and a special mustard fermented in the soundwaves of whale songs. At $4,850 per serving, each sandwich comes with a certificate of authenticity and a small music box that plays a custom composition based on the molecular structure of its ingredients."
};