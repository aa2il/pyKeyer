%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% rc.m - J.B.Attili - 2020

% Octave code to test raised cosine tapering

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

close all
clear all
more off

disp 'Hey'

WPM=20
fs = 48000              # Playback rate
fo=700

T=5e-3

dotlen=1.2/WPM
Ndit = fix( fs*dotlen + 0.5)
tt = (0:(Ndit-1)) / fs;
dit = sin(2*pi * fo * tt);

N = fix( fs*T + 0.5)
t = (0:(N-1)) / fs;
a = 0.5*(1+cos(2*pi * 0.5/T * t));
env = ones(1,Ndit);
env(1:N) = 1-a;
env(end-N+1:end)=a;

dit = env .* dit;

figure
%plot(t,a)
%plot(tt,env)
plot(tt,dit)
