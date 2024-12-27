from peak_picking.hierarchy import Hierarchy

def group_related_sequences(sequences, length, hierarchy=None):
    """
    Group sequences that have the same non-N elements together.
    If hierarchy is provided, sort sequences within groups by their values.
    """
    groups = {}
    for seq in sequences:
        # Get non-N elements in order of appearance
        non_n = tuple(x for x in seq if x != 'N')
        if non_n not in groups:
            groups[non_n] = []
        groups[non_n].append(seq)

    # Return groups in correct order
    result = []
    for non_n in sorted(groups.keys()):
        # For each group, get all sequences with these non-N elements
        group = groups[non_n]
        # If hierarchy is provided, sort by sequence values
        if hierarchy and hierarchy.sequence_values:
            group.sort(key=lambda x: (hierarchy.sequence_values.get(x, float('inf'))))
        else:
            group.sort()
        result.append(group)
    return result

def print_sequences_by_level(sequences, hierarchy):
    """
    Print sequences grouped by level and ordered by their values within groups.
    Also prints the sequence values if available.
    """
    # Group sequences by their number of non-null elements
    by_level = {}
    for seq in sequences:
        level = hierarchy.count_non_null(seq)
        if level not in by_level:
            by_level[level] = []
        # Convert to string but keep original sequence for value lookup
        by_level[level].append((seq, ''.join(seq)))

    # Print in descending order of non-null elements
    for level in sorted(by_level.keys(), reverse=True):
        sequences_at_level = by_level[level]
        print(f"\nSequences with {level} non-null elements ({len(sequences_at_level)}):")

        if level in [0, len(sequences_at_level[0][0])]:  # Full sequence or all-N sequence
            seq, seq_str = sequences_at_level[0]
            value = hierarchy.get_sequence_value(seq)
            value_str = f" (value: {value:.2f})" if value is not None else ""
            print(f"{seq_str}{value_str},")
        else:
            # Group related sequences together
            groups = group_related_sequences([seq for seq, _ in sequences_at_level],
                                          len(sequences_at_level[0][0]),
                                          hierarchy)
            for group in groups:
                formatted_group = []
                for seq in group:
                    value = hierarchy.get_sequence_value(seq)
                    seq_str = ''.join(seq)
                    if value is not None:
                        formatted_group.append(f"{seq_str} ({value:.2f})")
                    else:
                        formatted_group.append(seq_str)
                print(', '.join(formatted_group) + ',')

def main():
    # Create hierarchy and generate sequences
    h = Hierarchy(null_element='N')
    base_sequence = ('A', 'B', 'C', 'D', 'E')
    all_sequences = h.generate_all_descendants(base_sequence)

    # Set some example values (you would replace this with your actual values)
    example_values = {}
    for seq in all_sequences:
        # This is just an example - replace with your actual value assignment logic
        non_null_count = sum(bool(x != 'N')
                         for x in seq)
        example_values[seq] = non_null_count * 2.5 + len(seq)

    h.set_sequence_values(example_values)

    print("All sequences from ABCDE with preserved order:")
    print_sequences_by_level(all_sequences, h)

    return h, all_sequences

if __name__ == "__main__":
    main()
