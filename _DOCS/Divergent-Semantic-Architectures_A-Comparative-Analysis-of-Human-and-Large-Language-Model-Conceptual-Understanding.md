# Divergent Semantic Architectures: A Comparative Analysis of Human and Large Language Model Conceptual Understanding

The rapid emergence of Large Language Models (LLMs) has fundamentally altered the landscape of computational linguistics and cognitive science, necessitating a rigorous re-evaluation of what constitutes linguistic understanding. While these systems demonstrate a superficial mastery of human syntax and a vast associative capacity, empirical research increasingly identifies a profound divergence between the statistical representations utilized by machines and the grounded, referential conceptual systems characteristic of human cognition. The distinction lies not merely in the degree of accuracy but in the foundational mechanisms of meaning construction. Human understanding is inherently embodied, multimodal, and referential, whereas LLM "understanding" is distributional, unimodal, and statistical. This analysis synthesizes quantifiable evidence from academic studies to delineate the specific architectural and functional differences in how humans and LLMs process the meaning of words.

## The Epistemological Divide: Referential Grounding versus Distributional Statistics

The primary distinction between human and artificial linguistic processing resides in the nature of semantic grounding. For humans, language is a tool for navigating a physical and social reality. Words serve as symbolic pointers to referents—entities, actions, and sensations—grounded in sensorimotor experience. This referential framework is established through multimodal integration during early development, where a child associates the auditory or visual symbol "red" with the direct visual perception of a specific wavelength of light or the tactile experience of a "warm" object.

In contrast, LLMs are built upon the distributional hypothesis, which posits that the meaning of a word is entirely defined by its statistical distribution across a text corpus. This creates what researchers term the Vector Grounding Problem (VGP), a modern iteration of the classical Symbol Grounding Problem. While humans ground symbols in the world, LLMs ground vectors in other vectors. This leads to a system that is "domain-closed," capable of manipulating linguistic forms based on their probability of co-occurrence but lacking any intrinsic link to the extra-linguistic reality those forms represent.

| Feature | Human Semantic System | LLM Semantic System |
| :--- | :--- | :--- |
| **Foundational Mechanism** | Sensorimotor grounding and social interaction | Statistical co-occurrence in text corpora |
| **Grounding Type** | Direct (perceptual, motor, affective) | Indirect (verbal, derived, parasitic) |
| **Primary Objective** | Navigation of reality and goal achievement | Next-token prediction and pattern mimicry |
| **Information Source** | Multimodal (sight, sound, touch, etc.) | Unimodal (static text/discrete tokens) |
| **Meaning Basis** | Referential and Truth-conditional | Distributional and Associative |

The implications of this divide are quantifiable. Human communication relies on the establishment of "common ground"—a shared belief system about the world that is updated in real-time through interaction. In referential communication tasks, such as the director-matcher paradigm, humans demonstrate high efficiency and "lexical entrainment," where they adapt their vocabulary to their partner to ensure mutual understanding. LLMs, even when achieving near-human task accuracy, fail to replicate these patterns of common ground formation. They lack the ability to use meta-linguistic references, such as "the one we discussed earlier," in a way that reflects a true shared mental state, suggesting that their "understanding" of a word remains static and decoupled from the dynamic, negotiated nature of human meaning.

## Quantitative Deviations in Lexical Organization

The organization of the mental lexicon—the internal "dictionary" that defines the relationships between words—provides a measurable window into the differences between human and machine cognition. Studies comparing LLM internal states to large-scale human word association data, such as the Small World of Words (SWOW) project, reveal significant structural anomalies.

### Clustering, Diversity, and Semantic Space Collapse

One of the most robust quantifiable findings is the difference in diversity and clustering within the semantic space. When subjected to Kullback-Leibler (KL) divergence analysis, LLM-generated word associations show significant deviations from human patterns across various demographic groups. LLM lexicons tend toward greater clustering and reduced diversity, a phenomenon often described as "semantic space collapse".

This collapse indicates that LLMs prioritize high-probability regions of the semantic space, effectively "over-smoothing" the nuances of language. While a human mental lexicon is rich with idiosyncratic, culturally specific, and affective associations, LLMs converge on the most frequent patterns found in their training data. This lack of collective diversity is particularly evident in creative tasks, where human authors consistently exhibit higher originality, while LLMs excel at maintaining "execution quality" based on standard, predictable linguistic patterns.

### The Information Bottleneck Principle

The Information Bottleneck (IB) principle offers a mathematical framework for quantifying how LLMs and humans navigate the trade-off between information compression and meaning preservation. Human categorization systems balance the need to reduce cognitive load with the necessity of preserving rich, multidimensional structural detail.

Quantitative analysis of embeddings from over 40 LLMs reveals that these models achieve mathematically "optimal" information-theoretic efficiency, yet they do so by sacrificing the semantic nuance that is central to human understanding. Humans maintain "inefficient" representations that preserve typicality gradients—the understanding that some members of a category are more "representative" than others (e.g., a "robin" being more representative of "bird" than a "penguin"). LLMs frequently miss these fine-grained distinctions, treating categorical boundaries as aggressive statistical frontiers rather than graded, flexible concepts.

| Metric Category | Human Trajectory | LLM Trajectory (SOTA Models) |
| :--- | :--- | :--- |
| **Lexical Diversity** | High (Context-specific) | Low (Probability-centered) |
| **Semantic Clustering** | Distributed and Nuanced | Aggressive and Concentrated |
| **Typicality Capture** | Graded (Robin > Penguin) | Coarse/Binary (Member/Non-member) |
| **Compression Goal** | Meaning preservation/Utility | Statistical efficiency/Loss minimization |
| **Adaptability** | High (Cultural/Contextual shift) | Low (Stuck in training distribution) |

## Disambiguation and the Polysemy Paradox

The ability to resolve lexical ambiguity—where a single word has multiple meanings—is a hallmark of human semantic competence. Humans resolve these ambiguities effortlessly by integrating context, world knowledge, and pragmatic inference. While LLMs can generate text that appears to handle ambiguity, their performance on explicit Word Sense Disambiguation (WSD) tasks reveals a different underlying reality.

### Infrequent Senses and Frequency Bias

LLMs demonstrate a pronounced frequency bias that distinguishes them from human comprehenders. In WSD benchmarks, leading models such as GPT-4o and DeepSeek-V3 achieve high accuracy (up to 98%) when asked to explain the meaning of words in a general, unconstrained setting. However, their accuracy drops significantly when presented with "infrequent senses"—the less common meanings of a polysemous word.

This quantifiable drop suggests that LLMs do not "understand" the word sense through a deep conceptual model, but rather through a probability map weighted toward the most common usage in their training data. A human reader can utilize a few contextual cues to instantly shift to a rare sense of a word, whereas the LLM’s internal state is heavily anchored to its most frequent statistical occurrences.

## Metalinguistic Inconsistency and Representational Disconnect

Perhaps the most compelling evidence of a "different understanding" is the metalinguistic gap: the disconnect between what a model claims about a word and how it represents that word internally. Research utilizing the Haber and Poesio dataset compared three metrics: Human Rating Scores (HRS), Model Rating Scores (MRS) generated via text prompting, and Cosine Similarity Scores (CSS) derived from internal embeddings.

| Model Comparison | MRS-HRS Correlation ($r_s$) | CSS-HRS Correlation ($r_s$) | MRS-CSS Consistency |
| :--- | :---: | :---: | :---: |
| **LLaMA-3-8B** | 0.616 | 0.016 | 0.118 |
| **Gemma-7B** | 0.446 | −0.002 | 0.056 |
| **Mistral-7B** | 0.404 | −0.020 | 0.042 |

The data indicates that while models can mimic human similarity judgments in their generated text (MRS), their internal vector representations (CSS) show almost no alignment with human perception. The correlation between the model's textual output and its internal representations is also extremely low (<0.12). This quantifiable gap proves that the model's "answer" is not derived from a human-like internal semantic space; instead, it is a secondary generative task that produces a "plausible" answer without a corresponding foundation in the model's primary representational geometry.

## Neurocognitive and Biological Divergence

The study of Brain-LLM alignment provides a physiological baseline for comparing human and machine "understanding." By mapping model activations to fMRI, EEG, and MEG recordings, researchers can quantify the extent to which LLMs mirror the neurobiological processes of language comprehension.

### Linear Predictivity and the N400 Component

Large-scale examinations show that the internal states of high-performing LLMs are systematically predictive of activity in the human language network. The alignment score is often operationalized as the Pearson correlation between true and predicted brain activity, normalized by a noise ceiling: $score = r/c$. Models such as GPT-2 and more recent transformers have achieved near-ceiling fits on some fMRI and ECoG datasets, suggesting they capture some aspects of hierarchical feature processing.

Furthermore, LLM surprisal values correlate with the N400 ERP component, a neural marker of semantic processing difficulty. However, deeper analysis reveals a "discrete vs. continuous" processing discrepancy. While human brains exhibit continuous, iterative, and recurrent processing during reading, LLMs demonstrate feedforward, "discrete, stage-end bursts" of activity. The brain processes a sentence iteratively, with all areas active concurrently, whereas a transformer processes sequentially through layers for a single token.

## The Scaling Paradox

A critical quantifiable anomaly in this field is the "scaling paradox." While making LLMs larger generally increases their alignment with high-level fMRI brain activity patterns, it often decreases their alignment with human behavioral measures like reading times and eye-movement patterns. As models are optimized for the mathematical goal of next-token prediction on trillions of words, they become more efficient at a task that exceeds human capabilities, causing them to drift away from the "satisficing" and memory-constrained strategies that define human linguistic cognition.

| Alignment Metric | LLM-Brain Alignment Observation | Divergence Note |
| :--- | :--- | :--- |
| **fMRI Predictivity** | Increases with model size | Driven by high-level semantic features |
| **Reading Time Fit** | Peaks at ≈2B tokens | Larger models exceed human processing heuristics |
| **Processing Path** | Feedforward Layer-wise | Human: Recurrent/Simultaneous |
| **N400 Alignment** | Strong at ≈400ms | Shared mechanisms for surprisal only |
| **Attribution Spread** | Opposing trends (BA vs NWP) | Brain alignment relies more on discourse/context |

## Logic, Quantifiers, and the Limits of Distributionalism

The conventional wisdom that distributional models should excel at context-sensitive, graded meanings while struggling with formal logic is challenged by recent studies on quantifiers. Research comparing LLM and human judgments on "vague" quantifiers (e.g., "many") versus "exact" quantifiers (e.g., "more than half") reveals an unexpected reversal.

### The Vague-Exact Asymmetry

In comparative studies, LLMs consistently align more closely with human judgments on exact quantifiers than on vague ones. Human interpretation of "many" is highly context-sensitive, relying on world knowledge, previous linguistic exposure, and social cues to set a proportional threshold. LLMs, despite their massive scale, struggle to replicate the flexible, heuristic-based thresholds humans use for these underspecified terms.

Conversely, their better performance on exact quantifiers suggests that LLMs are more adept at capturing truth-conditional logic that is explicitly represented in the text, rather than the "vague" linguistic conventions that distributional semantics was originally theorized to model best. This implies that an LLM’s "understanding" of a quantifier is more of a mathematical calculation based on lexical patterns than a cognitive approximation of quantity.

## Syntactic Heuristics and the Illusion of Comprehension

The perception that LLMs understand word meaning is often an artifact of their syntactic proficiency. Humans generally process meaning and syntax in an integrated fashion, with a priority on semantic intent. Research at MIT has identified a failure mode in LLMs where they mistakenly link certain grammatical patterns—"syntactic templates"—with specific topics.

### The Syntactic Template Trap

When an LLM learns to associate a pattern (e.g., adverb/verb/proper noun/verb) with a specific domain like geography, it may provide a correct answer even when the query is nonsense, provided the syntax is maintained. For instance, a model given "Quickly sit Paris clouded?" might respond with "France" simply because it has associated that part-of-speech structure with country-related questions.

This "syntactic bias" represents a fundamental divergence from human understanding. A human would immediately identify the query as nonsensical, whereas the LLM overrides semantic reasoning in favor of learned syntactic correlations. This reliance on "familiar phrasing" over conceptual understanding reduces the reliability of LLMs in edge cases and allows for adversarial "jailbreaking" by phrasing harmful requests in the syntactic templates the model associates with "safe" or educational datasets.

| Failure Mode | Mechanism | Quantifiable Impact |
| :--- | :--- | :--- |
| **Syntactic Over-reliance** | Pattern matching vs. Reasoning | Model answers nonsense with "correct" facts |
| **Semantic Inconsistency** | Disconnect between output and vectors | Correlation between MRS and CSS < 0.12 |
| **Grounding Absence** | No sensorimotor feedback loop | Failure in non-linguistic spatial/causal tasks |
| **Frequency Dominance** | Bias toward head of distribution | Significant drop in accuracy for infrequent senses |
| **Abstract Divergence** | Struggle with affective features | Spearman rho < 0.48 for "Iconicity" |

## Communicative Performance and Cognitive Load

The divergent nature of LLM understanding is further evidenced by its impact on human communication. In psycholinguistic experiments comparing AI-powered translation to human translation, semantic accuracy for AI tools like DeepL and Google Translate was found to be approximately 78%, compared to 94% for human translators. More critically, humans interacting with AI-generated text showed different physiological signatures of processing.

### Eye-Tracking and Cognitive Load

Eye-tracking data reveals that human readers experience a higher cognitive load when processing AI output, characterized by longer reaction times, altered saccade patterns, and an increased reliance on re-reading. This suggests that even when AI-generated text is grammatically fluent, its "semantic texture" is slightly misaligned with human cognitive expectations, forcing the brain to exert more effort to extract a coherent meaning. Qualitative interviews also point to a phenomenon of "adaptive communication," where human users simplify their own language to match the perceived limitations of the AI, further highlighting the communicative asymmetry.

## Synthesizing the Divergence: From Mimicry to Model

The cumulative quantifiable evidence establishes that Large Language Models operate under a semantic paradigm that is fundamentally distinct from human cognition. While humans possess a "deep" understanding characterized by referential grounding, multimodal integration, and a truth-conditional world model, LLMs possess a "functional" or "distributional" understanding characterized by statistical association and syntactic heuristics.

The divergence is measurable across multiple dimensions: the lack of diversity in internal lexical networks, the profound disconnect between generated text and internal vector representations, the failure to resolve infrequent word senses, and the drift away from human biological processing patterns as models scale. Furthermore, the tendency of these models to rely on syntactic templates rather than semantic reasoning confirms that their "understanding" is a sophisticated form of pattern matching that lacks the intentionality and grounding of human thought.

The future of AI-human alignment will require more than mere scaling or instruction tuning. As researchers identify these specific points of divergence—such as the frequency-polysemy tradeoff in Martin’s Law or the efficiency-nuance tradeoff in the Information Bottleneck principle—the focus must shift toward architectural innovations that can bridge the grounding gap. Until then, LLMs serve as powerful mirrors of human language distribution but remain fundamentally different from the human minds that created that distribution. Their "meaning" is an emergent property of loss minimization, while human meaning is an emergent property of lived experience.

The quantifiable evidence from academic studies consistently shows that while LLMs can emulate the output of human language, they do so through a process that is structurally and functionally non-human. This distinction has profound implications for the trust, reliability, and deployment of these systems in domains requiring genuine semantic comprehension, such as clinical assistance, legal reasoning, and scientific discovery, where the "meaning" of a word must be tethered to a stable and verifiable truth in the world.

## References

- [Language writ large: LLMs, ChatGPT, meaning, and understanding - Frontiers](https://frontiersin.org)
- [Language writ large: LLMs, ChatGPT, meaning, and understanding - PMC](https://pmc.ncbi.nlm.nih.gov)
- [Cognitive Alignment Between Humans and LLMs Across Multimodal Domains - ResearchGate](https://researchgate.net)
- [Are LLMs Models of Distributional Semantics? A Case Study on Quantifiers - arXiv](https://arxiv.org)
- [Distributional Semantics in Language Models: A Comparative Analysis - Medium](https://medium.com)
- [The Vector Grounding Problem - arXiv](https://arxiv.org)
- [Will multimodal large language models ever achieve deep understanding of the world? - Frontiers](https://frontiersin.org)
- [LVLMs and Humans Ground Differently in Referential Communication - arXiv](https://arxiv.org)
- [Human-likeness of LLMs in the Mental Lexicon - ACL Anthology](https://aclanthology.org)
- [Human vs. LLM Creativity: A Comparative Analysis of Task-Dependent Asymmetry and Linguistic Mechanisms - MDPI](https://mdpi.com)
- [From Tokens to Thoughts: How LLMs and Humans Trade Compression for Meaning - arXiv](https://arxiv.org)
- [Do Large Language Models Understand Word Senses? - arXiv](https://arxiv.org)
- [Lost in Disambiguation: How Instruction-Tuned ... - ACL Anthology](https://aclanthology.org)
- [Brain–LLM Alignment - Emergent Mind](https://emergentmind.com)
- [Large Language Models Show Signs of Alignment with Human Neurocognition During Abstract Reasoning - arXiv](https://arxiv.org)
- [Revealing emergent human-like conceptual representations from language prediction - Semantic Scholar](https://semanticscholar.org)
- [Transformer-Based Language Model Surprisal Predicts Human Reading Times Best with About Two Billion Training Tokens - ResearchGate](https://researchgate.net)
- [Fine-grained Analysis of Brain-LLM Alignment through Input Attribution - arXiv](https://arxiv.org)
- [Psycholinguistics and Artificial Intelligence - Stackademic](https://blog.stackademic.com)
- [Researchers discover a shortcoming that makes LLMs less reliable - MIT News](https://news.mit.edu)
- [How well do large language models mirror human cognition of word concepts? - PMC](https://pmc.ncbi.nlm.nih.gov)
- [Emergent Lexical Semantics in Neural Language Models: Testing Martin's Law on LLM-Generated Text - arXiv](https://arxiv.org)
