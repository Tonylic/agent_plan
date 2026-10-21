#!/usr/bin/perl
use strict; use warnings;
my ($sp, $mode) = @ARGV;   # mode: local | artifact
sub slurp { my $f = shift; open my $h, '<:raw', $f or die "$f: $!"; local $/; my $c = <$h>; close $h; return $c; }
sub esc { my $s = shift; $s =~ s/&/&amp;/g; $s =~ s/</&lt;/g; $s =~ s/>/&gt;/g; return $s; }
sub cmd {
  my $s = esc(shift);
  my @out;
  for my $l (split /\n/, $s, -1) {
    if ($l =~ /^(\s*)(#.*)$/) { $l = "$1<span class=\"c\">$2</span>"; }
    elsif ($l =~ /^(.*?\S)(\s{2,}#\s.*)$/) { $l = "$1<span class=\"c\">$2</span>"; }
    push @out, $l;
  }
  return join "\n", @out;
}
my $head = slurp("$sp/shell-head.html");
my $body = slurp("$sp/body.tpl.html");
my $js   = slurp("$sp/shell-script.html");
$body =~ s/\@\@CMD\n(.*?)\n\@\@END/cmd($1)/gse;
$body =~ s/\@\@FILE:([^@]+)\@\@/do { my $c = slurp("$sp\/happy-config\/$1"); $c =~ s{\n+\z}{}; esc($c) }/ge;
die "unreplaced marker\n" if $body =~ /\@\@(CMD|END|FILE)/;
if ($mode eq 'local') {
  my ($title) = $head =~ /(<title>.*?<\/title>)/s;
  $head =~ s/<title>.*?<\/title>\n?//s;
  print "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n$title\n$head</head>\n<body>\n$body\n$js</body>\n</html>\n";
} else {
  print "$head\n$body\n$js";
}
