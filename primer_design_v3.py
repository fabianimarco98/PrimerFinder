import os
import primer3

def get_user_input(prompt, input_type=str, validation=None):
    while True:
        user_input = input(prompt)
        try:
            user_input = input_type(user_input)
            if validation and not validation(user_input):
                raise ValueError
            return user_input
        except ValueError:
            print(f"Invalid input. Please enter a valid {input_type.__name__}.")

def global_args_design(min_amplicon_size, max_amplicon_size, num_primers):
    # Default global parameters for primer design
    global_args = {
        'PRIMER_OPT_SIZE': 20,
        'PRIMER_PICK_INTERNAL_OLIGO': 1,
        'PRIMER_INTERNAL_MAX_SELF_END': 8,
        'PRIMER_MIN_SIZE': 18,
        'PRIMER_MAX_SIZE': 25,
        'PRIMER_OPT_TM': 52.0,
        'PRIMER_MIN_TM': 48.0,
        'PRIMER_MAX_TM': 56.0,
        'PRIMER_MIN_GC': 20.0,
        'PRIMER_MAX_GC': 80.0,
        'PRIMER_MAX_POLY_X': 100,
        'PRIMER_INTERNAL_MAX_POLY_X': 100,
        'PRIMER_SALT_MONOVALENT': 50.0,
        'PRIMER_DNA_CONC': 50.0,
        'PRIMER_MAX_NS_ACCEPTED': 0,
        'PRIMER_MAX_SELF_ANY': 12,
        'PRIMER_MAX_SELF_END': 8,
        'PRIMER_PAIR_MAX_COMPL_ANY': 12,
        'PRIMER_PAIR_MAX_COMPL_END': 8,
        'PRIMER_PRODUCT_SIZE_RANGE': [[min_amplicon_size, max_amplicon_size]],  # Set the amplicon size range
        'PRIMER_NUM_RETURN': num_primers  # Number of primers to return for each direction
    }

    print("\nDefault global parameters for primer design:")
    for key, value in global_args.items():
        print(f"{key}: {value}")

    modify_params = get_user_input("Do you want to modify any parameters? (yes/no): ", str, lambda x: x.lower() in ['yes', 'no']).lower()
    if modify_params == 'yes':
        while True:
            param_to_modify = get_user_input("Enter the parameter name you want to modify (or 'done' to finish): ", str)
            if param_to_modify.lower() == 'done':
                break
            if param_to_modify in global_args:
                new_value = get_user_input(f"Enter the new value for {param_to_modify}: ", type(global_args[param_to_modify]), lambda x: True)
                global_args[param_to_modify] = new_value
            else:
                print(f"{param_to_modify} is not a valid parameter name.")
                
    return global_args

def primer_feedback(primer_seq):
    primer_seq = primer_seq.upper()  # Convert to uppercase
    gc_content = 100 * (primer_seq.count('G') + primer_seq.count('C')) / len(primer_seq)
    tm = primer3.calc_tm(primer_seq)
    return gc_content, tm

def fragments_design(gene, a):
    while True:
        num_primers = get_user_input("Insert the number of primers you want to design: ", int, lambda x: x > 0)
        fragments = []
        for n in range(num_primers):
            while True:  # Loop until valid start and end are provided
                try:
                    start = get_user_input(f"Insert the start of fragment {n+1}: ", int)
                    end = get_user_input(f"Insert the end of fragment {n+1}, max: {len(gene)}: ", int)
                    print(f"Fragment {n+1}: from {a+start} to {a+end} of the initial vector, total size: {(a+end)-(a+start)}")
                    if start >= end or start < 0 or end > len(gene):
                        raise ValueError("Invalid fragment coordinates.")
                    length = end - start
                    fragments.append((start, length))
                    break  # Break the loop if valid input is provided
                except ValueError as e:
                    print()
                    print(f"Error: {e}. Please enter valid integers for the start and length of the fragment within the sequence range.")
                    print()
        return fragments, num_primers

def primer_design(seq, region_start, region_length, global_args):
    if region_start + region_length > len(seq):
        raise ValueError("The specified region exceeds the length of the sequence.")
    
    seq_args = {
        'SEQUENCE_ID': 'gene',
        'SEQUENCE_TEMPLATE': seq,
        'SEQUENCE_INCLUDED_REGION': [region_start, region_length],
    }

    primers = primer3.bindings.design_primers(seq_args, global_args)
    
    primer_feedback_dict = {}
    for i in range(global_args['PRIMER_NUM_RETURN']):
        forward_key = f'PRIMER_LEFT_{i}_SEQUENCE'
        reverse_key = f'PRIMER_RIGHT_{i}_SEQUENCE'
        if forward_key in primers and reverse_key in primers:
            forward_primer = primers[forward_key]
            reverse_primer = primers[reverse_key]
            forward_gc, forward_tm = primer_feedback(forward_primer)
            reverse_gc, reverse_tm = primer_feedback(reverse_primer)
            primer_feedback_dict[forward_key] = (forward_primer, forward_gc, forward_tm)
            primer_feedback_dict[reverse_key] = (reverse_primer, reverse_gc, reverse_tm)
        else:
            print(f"Warning: Primer {i+1} could not be designed.")
    
    return primers, primer_feedback_dict

def save_primers(primer_dict):
    save_path = get_user_input("Insert the path where you want to save the primers: ").strip("\"")
    save_path = save_path.replace("\\", "/")
    try:
        with open(save_path, "w") as file:
            for key, value in primer_dict.items():
                file.write(f"{key}: {value[0]} {value[1]}\n")
        return print(f"Primers saved successfully to {save_path}")
    except IOError as e:
        return print(f"Error writing to file: {e}")

def main():
    while True:
        path = get_user_input("Insert the path of the FASTA file containing the sequence: ").strip("\"")
        path = path.replace("\\", "/")
        
        if not os.path.isfile(path):
            print("The provided path is not valid. Please provide a valid file path.")
            continue
        
        try:
            with open(path, 'r') as file:
                seq = file.read()
                if not seq:
                    raise ValueError("The file is empty.")
                break
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")
            continue

    while True:
        try:
            a, b = input(f"Insert the bp where the gene starts and finishes (max: {len(seq)}) separated by space: ").split()
            a = int(a)
            b = int(b)
            if a < 0 or b > len(seq) or a >= b:
                raise ValueError("The start and end positions must be within the sequence length and start should be less than end.")
            break
        except ValueError:
            print("Please insert valid numbers within the sequence length range.")
            continue

    gene = seq[a:b]
    gene = gene.replace('\n', '')

    fragments, num_primers = fragments_design(gene, a)

    while True:
        min_amplicon_size = get_user_input("Insert the min amplicon size: ", int, lambda x: x > 0)
        max_amplicon_size = get_user_input("Insert the max amplicon size: ", int, lambda x: x > 0)
        if max_amplicon_size > min(length for _, length in fragments):
            print(f"Max amplicon size cannot be greater than the length of the smallest fragment ({min(length for _, length in fragments)}).")
        else:
            break

    global_args = global_args_design(min_amplicon_size, max_amplicon_size, num_primers)

    primer_dict = {}
    for i, (start, length) in enumerate(fragments, start=1):
        try:
            primers, feedback = primer_design(gene, start, length, global_args)
            print(f"Fragment {i}:")
            for j in range(num_primers):
                forward_key = f'PRIMER_LEFT_{j}_SEQUENCE'
                reverse_key = f'PRIMER_RIGHT_{j}_SEQUENCE'
                if forward_key in feedback and reverse_key in feedback:
                    print(f"Forward Primer {j+1}: {feedback[forward_key][0]} (GC%: {feedback[forward_key][1]:.2f}, Tm: {feedback[forward_key][2]:.2f})")
                    print(f"Reverse Primer {j+1}: {feedback[reverse_key][0]} (GC%: {feedback[reverse_key][1]:.2f}, Tm: {feedback[reverse_key][2]:.2f})")
                    print()
                    primer_dict[f"F_{i}_P_{j+1}"] = [feedback[forward_key][0], feedback[reverse_key][0]]
        except ValueError as e:
            print(f"Error in fragment {i}: {e}")
            continue
    
    print()
    choice = get_user_input("Do you want to save the primers? (yes/no): ", str, lambda x: x.lower() in ['yes', 'no']).lower()
    if choice == 'yes':
        save_primers(primer_dict)
    elif choice == 'no':
        print("Primers not saved.")
    else:
        print("Invalid choice. Primers not saved.")

if __name__ == '__main__':
    main()