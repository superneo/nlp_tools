#!/usr/bin/perl

use strict;
use warnings;
use utf8;
use HTML::Entities;
use Encode qw/encode decode/;
use File::Path 'rmtree';

sub trim { my $s = shift; $s =~ s/^\s+|\s+$//g; return $s };

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";

my ($raw_corpora_dir, $cleaned_corpora_dir) = @ARGV;

if (2 != scalar @ARGV || not defined $raw_corpora_dir || not defined $cleaned_corpora_dir) {
    print "[Usage] $0 [raw corpus directory] [cleaned corpus directory]\n";
    exit 1;
}

die "[ERROR] raw corpus directory $raw_corpora_dir does not exist\n"
    unless (-d $raw_corpora_dir);

if (-d $cleaned_corpora_dir) {
    rmtree($cleaned_corpora_dir);
}

die "[ERROR] failed to make cleaned corpus directory $cleaned_corpora_dir: $!\n"
    unless (mkdir $cleaned_corpora_dir);

# characters/symbols to remove globally in each line (some may require to be escaped)
my @del_chars = qw ( ○ ▴ );
my $pattern = join("|", @del_chars);

opendir(RAW_CORPORA_DIR, $raw_corpora_dir)
    or die "[ERROR] failed to open $raw_corpora_dir: $!\n";
opendir(CLEANED_CORPORA_DIR, $cleaned_corpora_dir)
    or die "[ERROR] failed to open $cleaned_corpora_dir: $!\n";

my @raw_corpora = grep {-f "$raw_corpora_dir/$_" && /^.*\.txt$/} readdir(RAW_CORPORA_DIR);

foreach my $corpus (@raw_corpora) {
    print "[processing file] $corpus\n";

    open(my $ifh, '<:encoding(UTF-8)', "$raw_corpora_dir/$corpus")
        or die "Could not open file '$raw_corpora_dir/$corpus' $!";
    open(my $ofh, '>:encoding(UTF-8)', "$cleaned_corpora_dir/$corpus")
        or die "Could not open file '$cleaned_corpora_dir/$corpus' $!";

    while (my $line = <$ifh>) {
        next if ($line !~ m/\p{InHangul_Syllables}/);
        next if ($line =~ m/BR.*\.txt.*원본:.*\.hwp/);  # ex) BRBB0062.txt, 원본:bb93b002.hwp
        chomp $line;
        $line = decode_entities($line);

        # text cleaning
        $line =~ s/^\(([^\(\)]+)\)$/$1/g;
        $line =~ s/::+//g;  # for cases like "그~ 김치후선생::이"
        $line =~ s/(\p{InHangul_Syllables})~([\s\p{P}])/$1$2/g;  # ex) "인민들과 만나지 않고 이~ 저::~,"
        $line =~ s/\`/'/g;
        $line =~ s/[「」]/"/g;
        $line =~ s/[【】◀▶]//g;
        $line =~ s/^" | " //g;  # caution
        $line =~ s/ ; | - / /g;
        $line =~ s/(\p{L})_(\p{L})/$1 $2/g;
        # for cases of literary corpora like "▴ 오빠 = 별로 없다."
        $line =~ s/^(\>\> |\*+ |◆ ?|▴ ?|◇ ?|\<\> +|● ?|── +|\|\| +|\! +)(\p{InHangul_Syllables}+\s*=\s*)?//;
        $line =~ s/$pattern//g;
        $line =~ s/<[^<>]+$|^[^<>]+>//g;
        $line =~ s/<[^\"<>]*\"((?:[^\"\p{InHangul_Syllables}]*\p{InHangul_Syllables}+[^\"\p{InHangul_Syllables}]*)+)\"[^\"<>]*>/$1/g;
        $line =~ s/<((?:[^<\/>\p{InHangul_Syllables}]*\p{InHangul_Syllables}+[^<\/>\p{InHangul_Syllables}]*)+)>/$1/g;
        $line =~ s/(<\/?(div|br|p|li|dt|dd).*?\/?>\s*)+/ /ig;
        $line =~ s/<[^<>]+>//g;
        $line =~ s/ / /g;  # nbsp
        $line =~ s/\x{FEFF}//g;  # zero width nbsp
        $line =~ s/ +/ /g;
        $line = trim $line;
        $line =~ s/\,$//;  # for colloquial corpora
        $line =~ s/^- | -$//g;  # for colloquial corpora
        $line =~ s/\. +"$/\."/;
        $line =~ s/(\d+)\. +(\d+)%/$1\.$2%/g;  # for cases of literary corpora like "49. 4%""
        $line =~ s/""+//g;
        next if ($line =~ m/^\s*$/);

        print $ofh $line."\n";
    }

    close($ofh);
    close($ifh);
}

closedir(CLEANED_CORPORA_DIR);
closedir(RAW_CORPORA_DIR);

