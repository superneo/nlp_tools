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

# TODO: corpus cleaning

closedir(CLEANED_CORPORA_DIR);
closedir(RAW_CORPORA_DIR);

