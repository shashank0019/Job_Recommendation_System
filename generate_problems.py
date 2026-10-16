#!/usr/bin/env python3
"""
Script to generate 200 diverse coding problems for the Problems component.
This creates a comprehensive problem dataset with various difficulties and topics.
"""

import json
import random

# Problem templates with different categories and difficulties
PROBLEM_TEMPLATES = [
    # Array Problems
    {
        "category": "Array",
        "difficulties": {
            "Easy": [
                "Find the maximum element in an array",
                "Check if array is sorted",
                "Remove duplicates from sorted array",
                "Find missing number in array",
                "Rotate array to the left",
                "Find second largest element",
                "Merge two sorted arrays",
                "Find intersection of two arrays",
                "Count frequency of each element",
                "Find pair with given sum"
            ],
            "Medium": [
                "Find subarray with maximum sum",
                "Rotate array by k positions",
                "Find majority element",
                "Spiral traversal of matrix",
                "Find peak element in array",
                "Sort array of 0s, 1s and 2s",
                "Maximum product subarray",
                "Find minimum in rotated sorted array",
                "Search in rotated sorted array",
                "Trapping rainwater problem"
            ],
            "Hard": [
                "Median of two sorted arrays",
                "Maximum sliding window",
                "Longest increasing subsequence",
                "Best time to buy and sell stock IV",
                "Count inversions in array",
                "Largest rectangle in histogram",
                "Minimum window substring",
                "Merge k sorted arrays",
                "Find kth smallest element",
                "Maximum sum rectangle in matrix"
            ]
        }
    },
    # String Problems
    {
        "category": "String", 
        "difficulties": {
            "Easy": [
                "Reverse a string",
                "Check if string is palindrome",
                "Count vowels and consonants",
                "Remove spaces from string",
                "Check if two strings are anagrams",
                "Find first non-repeating character",
                "Convert string to integer",
                "Check if strings are rotations",
                "Remove duplicates from string",
                "Find longest word in sentence"
            ],
            "Medium": [
                "Longest palindromic substring",
                "Group anagrams together",
                "String compression",
                "Find all permutations of string",
                "Longest substring without repeating characters",
                "Valid parentheses combinations",
                "Word break problem",
                "Minimum edit distance",
                "Longest common subsequence",
                "Pattern matching with wildcards"
            ],
            "Hard": [
                "Regular expression matching",
                "Shortest palindrome",
                "Word ladder problem",
                "Minimum window substring",
                "Interleaving strings",
                "Palindrome partitioning",
                "Edit distance with operations",
                "Longest valid parentheses",
                "String matching algorithms",
                "Suffix array construction"
            ]
        }
    },
    # Linked List Problems
    {
        "category": "Linked List",
        "difficulties": {
            "Easy": [
                "Reverse a linked list",
                "Find middle of linked list",
                "Detect cycle in linked list",
                "Remove duplicates from sorted list",
                "Merge two sorted lists",
                "Find length of linked list",
                "Delete node with given value",
                "Insert node at position",
                "Check if linked list is palindrome",
                "Find nth node from end"
            ],
            "Medium": [
                "Add two numbers as linked lists",
                "Remove nth node from end",
                "Rotate linked list",
                "Clone list with random pointers",
                "Intersection of two linked lists",
                "Sort linked list",
                "Reverse nodes in k-groups",
                "Flatten multilevel doubly linked list",
                "Split linked list in parts",
                "Odd even linked list"
            ],
            "Hard": [
                "Merge k sorted lists",
                "Reverse nodes in k-group",
                "LRU Cache implementation",
                "Skip list implementation",
                "Design linked list",
                "Memory efficient doubly linked list",
                "XOR linked list",
                "Self organizing list",
                "Josephus problem with linked list",
                "Unrolled linked list"
            ]
        }
    },
    # Tree Problems
    {
        "category": "Tree",
        "difficulties": {
            "Easy": [
                "Find height of binary tree",
                "Count nodes in binary tree",
                "Check if tree is balanced",
                "Find diameter of binary tree",
                "Level order traversal",
                "Check if trees are identical",
                "Find minimum depth",
                "Sum of all nodes",
                "Mirror a binary tree",
                "Find leaf nodes"
            ],
            "Medium": [
                "Lowest common ancestor",
                "Convert sorted array to BST",
                "Validate binary search tree",
                "Path sum problems",
                "Serialize and deserialize tree",
                "Boundary traversal",
                "Vertical order traversal",
                "Right view of binary tree",
                "Connect nodes at same level",
                "Construct tree from traversals"
            ],
            "Hard": [
                "Binary tree maximum path sum",
                "Recover binary search tree",
                "Count complete tree nodes",
                "Minimum cost tree from leaf values",
                "House robber in binary tree",
                "Distribute coins in binary tree",
                "Maximum width of binary tree",
                "Vertical order traversal II",
                "All nodes distance K",
                "Binary tree cameras"
            ]
        }
    },
    # Dynamic Programming
    {
        "category": "Dynamic Programming",
        "difficulties": {
            "Easy": [
                "Fibonacci sequence",
                "Climbing stairs",
                "House robber",
                "Maximum subarray sum",
                "Unique paths in grid",
                "Min cost climbing stairs",
                "Range sum query",
                "Best time to buy/sell stock",
                "Pascal's triangle",
                "Counting bits"
            ],
            "Medium": [
                "Coin change problem",
                "Longest increasing subsequence",
                "Edit distance",
                "Unique binary search trees",
                "Decode ways",
                "Maximum product subarray",
                "Word break",
                "Triangle minimum path",
                "Perfect squares",
                "Combination sum IV"
            ],
            "Hard": [
                "Regular expression matching",
                "Wildcard pattern matching",
                "Longest valid parentheses",
                "Maximal rectangle",
                "Best time to buy/sell stock III",
                "Interleaving string",
                "Scramble string",
                "Palindrome partitioning II",
                "Burst balloons",
                "Russian doll envelopes"
            ]
        }
    },
    # Graph Problems
    {
        "category": "Graph",
        "difficulties": {
            "Easy": [
                "Breadth first search",
                "Depth first search",
                "Check if path exists",
                "Count connected components",
                "Find center of star graph",
                "Valid graph tree",
                "Clone graph",
                "Find town judge",
                "Keys and rooms",
                "Flower planting with no adjacent"
            ],
            "Medium": [
                "Course schedule",
                "Number of islands",
                "Surrounded regions",
                "Pacific Atlantic water flow",
                "Word ladder",
                "Minimum spanning tree",
                "Detect cycle in directed graph",
                "Topological sorting",
                "Shortest path in binary matrix",
                "Network delay time"
            ],
            "Hard": [
                "Word ladder II",
                "Alien dictionary",
                "Critical connections",
                "Minimum cost to make connected",
                "Shortest path visiting all nodes",
                "Bus routes",
                "Swim in rising water",
                "Sliding puzzle",
                "Cracking the safe",
                "Similar string groups"
            ]
        }
    },
    # Hash Table Problems
    {
        "category": "Hash Table",
        "difficulties": {
            "Easy": [
                "Two sum using hash table",
                "Contains duplicate",
                "Single number",
                "Happy number",
                "Isomorphic strings"
            ],
            "Medium": [
                "Group anagrams",
                "Top K frequent elements", 
                "Subarray sum equals K",
                "4Sum problem",
                "Find all anagrams"
            ],
            "Hard": [
                "First missing positive",
                "Longest consecutive sequence",
                "Max points on a line",
                "Word pattern II", 
                "Alien dictionary"
            ]
        }
    },
    # Math Problems
    {
        "category": "Math",
        "difficulties": {
            "Easy": [
                "Palindrome number",
                "Roman to integer",
                "Plus one",
                "Sqrt(x)",
                "Power of two"
            ],
            "Medium": [
                "Integer to Roman",
                "Pow(x, n)",
                "Divide two integers",
                "Fraction to decimal",
                "Happy number"
            ],
            "Hard": [
                "Basic calculator III",
                "Max points on line",
                "Integer to English words",
                "Self crossing",
                "Valid number"
            ]
        }
    }
]

def generate_sample_data(problem_title, difficulty, topic):
    """Generate sample input/output based on problem type"""
    samples = []
    
    if "Two Sum" in problem_title or "pair" in problem_title.lower():
        samples.append({
            "input": "[2,7,11,15], 9",
            "output": "[0,1]",
            "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1]."
        })
    elif "array" in problem_title.lower() and "maximum" in problem_title.lower():
        samples.append({
            "input": "[-2,1,-3,4,-1,2,1,-5,4]",
            "output": "6", 
            "explanation": "The subarray [4,-1,2,1] has the largest sum 6."
        })
    elif "string" in problem_title.lower() and "palindrome" in problem_title.lower():
        samples.append({
            "input": "\"babad\"",
            "output": "\"bab\"",
            "explanation": "Note: \"aba\" is also a valid answer."
        })
    elif "linked list" in problem_title.lower() and "reverse" in problem_title.lower():
        samples.append({
            "input": "[1,2,3,4,5]",
            "output": "[5,4,3,2,1]",
            "explanation": "Reverse the linked list."
        })
    elif "tree" in problem_title.lower():
        samples.append({
            "input": "[3,9,20,null,null,15,7]",
            "output": "3",
            "explanation": "The maximum depth is 3."
        })
    else:
        # Generic samples based on difficulty
        if difficulty == "Easy":
            samples.append({
                "input": "[1,2,3,4,5]",
                "output": "15",
                "explanation": "Example calculation based on the problem."
            })
        elif difficulty == "Medium":
            samples.append({
                "input": "[[1,2],[3,4]]",
                "output": "10",
                "explanation": "Process the 2D input according to problem requirements."
            })
        else:  # Hard
            samples.append({
                "input": "Complex input structure",
                "output": "Optimized result",
                "explanation": "Advanced algorithm implementation required."
            })
    
    return samples

def generate_constraints(difficulty):
    """Generate constraints based on difficulty"""
    if difficulty == "Easy":
        return [
            "1 <= n <= 10^4",
            "-10^3 <= values <= 10^3",
            "Time complexity: O(n) expected",
            "Space complexity: O(1) preferred"
        ]
    elif difficulty == "Medium":
        return [
            "1 <= n <= 10^5", 
            "-10^6 <= values <= 10^6",
            "Time complexity: O(n log n) or better",
            "Space complexity: O(n) acceptable"
        ]
    else:  # Hard
        return [
            "1 <= n <= 10^6",
            "-10^9 <= values <= 10^9", 
            "Time complexity: O(n) or O(n log n) required",
            "Advanced algorithms and optimizations needed"
        ]

def generate_200_problems():
    """Generate 200 diverse coding problems"""
    problems = []
    problem_id = 1
    seen_titles = set()  # Track titles to avoid duplicates
    
    for template in PROBLEM_TEMPLATES:
        category = template["category"]
        
        for difficulty, titles in template["difficulties"].items():
            for title in titles:
                # Skip if we've already seen this title
                if title in seen_titles:
                    continue
                seen_titles.add(title)
                # Create additional topics related to the category
                if category == "Array":
                    topics = ["Array", random.choice(["Hash Table", "Two Pointers", "Sorting", "Binary Search"])]
                elif category == "String":
                    topics = ["String", random.choice(["Hash Table", "Two Pointers", "Sliding Window", "Trie"])]
                elif category == "Linked List":
                    topics = ["Linked List", random.choice(["Two Pointers", "Recursion", "Stack"])]
                elif category == "Tree":
                    topics = ["Tree", "Binary Tree", random.choice(["DFS", "BFS", "Recursion"])]
                elif category == "Dynamic Programming":
                    topics = ["Dynamic Programming", random.choice(["Array", "String", "Math"])]
                elif category == "Graph":
                    topics = ["Graph", random.choice(["BFS", "DFS", "Union Find", "Topological Sort"])]
                else:
                    topics = [category]
                
                problem = {
                    "id": str(problem_id),
                    "title": title,
                    "difficulty": difficulty,
                    "topics": topics,
                    "statement": {
                        "description": f"Solve the {title.lower()} problem efficiently. This is a {difficulty.lower()} level problem that requires understanding of {', '.join(topics).lower()} concepts.",
                        "samples": generate_sample_data(title, difficulty, category),
                        "constraints": generate_constraints(difficulty)
                    },
                    "languages": ["python", "javascript", "java", "cpp"]
                }
                
                problems.append(problem)
                problem_id += 1
                
                # Stop once we reach 200 problems
                if len(problems) >= 200:
                    break
            
            if len(problems) >= 200:
                break
        
        if len(problems) >= 200:
            break
    
    return problems[:200]  # Ensure exactly 200 problems

def main():
    """Generate and save 200 problems to JSON file"""
    print("Generating 200 diverse coding problems...")
    
    problems = generate_200_problems()
    
    # Save to JSON file
    output_file = "problems_dataset_200.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(problems, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Successfully generated {len(problems)} problems!")
    print(f"📁 Saved to: {output_file}")
    
    # Print summary statistics
    difficulties = {}
    categories = {}
    
    for problem in problems:
        diff = problem["difficulty"]
        difficulties[diff] = difficulties.get(diff, 0) + 1
        
        for topic in problem["topics"]:
            categories[topic] = categories.get(topic, 0) + 1
    
    print("\n📊 Problem Distribution:")
    print("By Difficulty:")
    for diff, count in sorted(difficulties.items()):
        print(f"  {diff}: {count} problems")
    
    print("\nTop Categories:")
    sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
    for category, count in sorted_categories[:10]:
        print(f"  {category}: {count} problems")
    
    print(f"\n🎯 Ready to update your Problems component!")
    print("Next steps:")
    print("1. The problems are saved in problems_dataset_200.json")
    print("2. Update your Problems.jsx component to load these problems")
    print("3. Your users will now have 200 diverse problems to solve!")

if __name__ == "__main__":
    main()