#!/usr/bin/perl

use strict;
use warnings;
use utf8;
use HTML::Entities;
use Encode qw/encode decode/;
use File::Path 'rmtree';
use Regexp::Common qw(URI);

sub trim { my $s = shift; $s =~ s/^\s+|\s+$//g; return $s };

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";

my ($raw_corpus_dir, $cleaned_corpus_dir) = @ARGV;

if (2 != scalar @ARGV || not defined $raw_corpus_dir || not defined $cleaned_corpus_dir) {
    print "[Usage] $0 [raw corpus directory] [cleaned corpus directory]\n";
    exit 1;
}

die "[ERROR] raw corpus directory $raw_corpus_dir does not exist\n"
    unless (-d $raw_corpus_dir);

if (-d $cleaned_corpus_dir) {
    rmtree($cleaned_corpus_dir);
}

die "[ERROR] failed to make cleaned corpus directory $cleaned_corpus_dir: $!\n"
    unless (mkdir $cleaned_corpus_dir);

opendir(RAW_CORPUS_DIR, $raw_corpus_dir)
    or die "[ERROR] failed to open $raw_corpus_dir: $!\n";
opendir(CLEANED_CORPUS_DIR, $cleaned_corpus_dir)
    or die "[ERROR] failed to open $cleaned_corpus_dir: $!\n";

open(RAW_CORPUS, "<:encoding(UTF-8)",
    "$raw_corpus_dir/kowiki-latest-pages-articles.xml")
    or die "[ERROR] failed to open kowiki-latest-pages-articles.xml: $!\n";
open(CLEANED_CORPUS, ">:encoding(UTF-8)",
    "$cleaned_corpus_dir/cleaned_korean_wiki_dumps.txt")
    or die "[ERROR] failed to open cleaned_korean_wiki_dumps.txt: $!\n";

my $raw_lines = 0;
my $cleaned_lines = 0;
while (my $line = <RAW_CORPUS>) {
    $raw_lines++;
    next if ($line !~ m/\p{InHangul_Syllables}/);
    chomp $line;
    $line = decode_entities($line);

    # text cleaning
    $line =~ s/$RE{URI}{HTTP}//g;  # delete all URLs matched
    $line =~ s/\[\[([^\|\[\]]+)\|([^\|\[\]]+)\]\]/$1 $2/g;
    $line =~ s/\[\[([^\[\]]+)\]\]/$1/g;
    $line =~ s/(^!)?colspan[^!\|\p{Hangul}]+\|//g;
    $line =~ s/'''([^\']+)'''/$1/g;
    $line =~ s/(\|\|\s*\d+\s*)+//g;
    $line =~ s/(\p{InHangul_Syllables})_(\p{InHangul_Syllables})/$1 $2/g;
    $line =~ s/<[^<>]+$|^[^<>]+>//g;
    $line =~ s/<[^<>]+>//g;
    $line =~ s/ / /g;  # nbsp
    $line =~ s/\x{FEFF}//g;  # zero width nbsp
    $line =~ s/ +/ /g;
    $line = trim $line;
    next if ($line =~ m/^\s*$/);

    print CLEANED_CORPUS $line."\n";
    $cleaned_lines++;
    print ("# lines processed: ".$cleaned_lines."\n") if ($cleaned_lines % 1000000 == 0);
}

print ("## total cleaned lines: ".$cleaned_lines." / ".$raw_lines."\n");

close(CLEANED_CORPUS);
close(RAW_CORPUS);

closedir(CLEANED_CORPUS_DIR);
closedir(RAW_CORPUS_DIR);

