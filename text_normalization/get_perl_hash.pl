#!/usr/bin/perl

use strict;
use warnings;
use utf8;

sub trim { my $s = shift; $s =~ s/^\s+|\s+$//g; return $s };

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";

my ($chars_to_normalize_file,) = @ARGV;

if (1 != scalar @ARGV || not defined $chars_to_normalize_file) {
    print "[Usage] $0 [chars_to_normalize list file path]\n";
    exit 1;
}

open(my $ifh, '<:encoding(UTF-8)', $chars_to_normalize_file)
    or die "Could not open file '$chars_to_normalize_file' $!";

print "my %chars_to_norm = (\n";
while(my $line = <$ifh>) {
    chomp $line;
    if ($line =~ m/^([^\t])\t([^\t]+?)(?:$|(?=(?:\/\/ )))/) {
        if ($2 eq '"' or $2 eq "'" or $2 eq "\$" or $2 eq "\%" or $2 eq "\&" or $2 eq "\\") {
            print "    \"$1\"\t=> \"\\$2\",\n";
        } else {
            print "    \"$1\"\t=> \"$2\",\n";
        }
    } else {
        print "[ERROR] invalid line encountered!!!\n\t$line\n";
        last;
    }
}
print ");\n";

close($ifh);

