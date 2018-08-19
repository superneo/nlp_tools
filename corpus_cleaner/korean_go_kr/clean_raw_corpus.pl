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
        chomp $line;
        $line = decode_entities($line);

        # text cleaning
        $line =~ s/::+//g;  # for cases like "그~ 김치후선생::이"
        $line =~ s/(\p{InHangul_Syllables})~([\s\p{P}])/$1$2/g;  # for cases like "인민들과 만나지 않고 이~ 저::~,"
        $line =~ s/(\p{L})_(\p{L})/$1$2/g;
        $line =~ s/<[^<>]+$|^[^<>]+>//g;
        $line =~ s/<[^\"<>]*\"((?:[^\"\p{InHangul_Syllables}]*\p{InHangul_Syllables}+[^\"\p{InHangul_Syllables}]*)+)\"[^\"<>]*>/$1/g;
        $line =~ s/<((?:[^<\/>\p{InHangul_Syllables}]*\p{InHangul_Syllables}+[^<\/>\p{InHangul_Syllables}]*)+)>/$1/g;
        $line =~ s/<[^<>]+>//g;
        $line =~ s/ / /g;  # nbsp
        $line =~ s/\x{FEFF}//g;  # zero width nbsp
        $line =~ s/ +/ /g;
        $line = trim $line;
        $line =~ s/\,$//;  # for only colloquial corpora
        next if ($line =~ m/^\s*$/);

        print $ofh $line."\n";
    }

    close($ofh);
    close($ifh);
}

closedir(CLEANED_CORPORA_DIR);
closedir(RAW_CORPORA_DIR);
