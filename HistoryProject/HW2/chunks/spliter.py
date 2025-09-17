def split_file(input_file, lines_per_file=1000):
    with open(input_file, "r", encoding="utf-8") as f:
        file_count = 1
        current_lines = []

        for i, line in enumerate(f, start=1):
            current_lines.append(line)

            if i % lines_per_file == 0:
                output_file = f"part_{file_count}.txt"
                with open(output_file, "w", encoding="utf-8") as out:
                    out.writelines(current_lines)
                print(f"Created {output_file} with {len(current_lines)} lines")
                file_count += 1
                current_lines = []

        # Write remaining lines (if not multiple of lines_per_file)
        if current_lines:
            output_file = f"part_{file_count}.txt"
            with open(output_file, "w", encoding="utf-8") as out:
                out.writelines(current_lines)
            print(f"Created {output_file} with {len(current_lines)} lines")


if __name__ == "__main__":
    split_file("links.txt", 1000)
