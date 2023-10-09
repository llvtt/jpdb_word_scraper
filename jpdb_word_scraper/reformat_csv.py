import csv


def main():
    input_filename = "jpdb_words.csv"
    output_filename = "jpdb_words_fixed.csv"
    with open(input_filename) as csvfile, open(output_filename, "w") as outputfile:
        reader = csv.reader(csvfile)
        writer = csv.writer(outputfile)

        next(reader)  # skip header row
        for line in reader:
            glossary, pos = line[2:4]
            formatted_gloss = f'<p class="pos">{pos}</p><p glass="glossary">{glossary}</p>'
            formatted_line = [
                line[0],
                line[1],
                formatted_gloss,
                *line[4:],
            ]
            writer.writerow(formatted_line)


if __name__ == '__main__':
    main()
