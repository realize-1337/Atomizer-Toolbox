    % Funtion zur Berechnung des Messvolumendurchmessers als Funtion der
    % Partikeltrajektorie und der Tropfengr��e unter der Ber�cksichtigung einer
    % Korrelation zwischen Burstl�nge und Tropfengr��e
    % Autor:    AS
    % Editor for Python implementation: David Maerker
    
    
    function [] = D_A_for_py(D, Ttime, LDA1, LDA4, f_1, f_2, ls_p, phi, path)
    
    % Einstellgr��en f�r USER innerhalb der Funktion***************************
    % diese Einstellungen gelten als Standardeinstellungen (erprobt)
    
    bingroesse = 5; %Gr��e eines bins angeben in �m
    bincount = 200; % min Tropfen / Bin f�r Fit (POW- & LOG - Fit) 
    
    % ENDE USER Einstellungen *************************************************
    
    % Start Funktion **********************************************************
    D = D';
    Ttime = Ttime';
    LDA1 = LDA1';
    LDA4 = LDA4';

    % Berechnung des Messvolumendurchmessers D_e als Funktion der Tropfenr��e
    % und der Partikeltrajektorie LDA1 und LDA 2 nach Gleichung 12.48 in
    % Albrecht et.al 
    
    beta = -f_2/f_1;
    ls_korr = ls_p/abs(beta);        %[�m]
    D_val = zeros(length(D),1);   %[�m]
    A_val = zeros(length(D),1);   %[�m^2]

    % NEW
    res = Ttime .* LDA1;
    sum1 = cumsum(res);

    for i=1:length(D)
        D_val(i) = (4/pi)*((ls_korr*sum1(end))/(ls_korr-cos(phi)*sum1(end)*abs(LDA4(i)/sqrt(LDA1(i)^2+LDA4(i)^2)))); % [�m]
    end
    
    % Ab hier ist D_e in [�m]
    
    for i=1:length(D)
       A_val(i) = (D_val(i)*ls_korr/sin(phi)) - (pi*(D_val(i)^2)/4/tan(phi)) * (abs(LDA4(i))/sqrt(LDA1(i)^2+LDA4(i)^2)); % [�m^2]
    end

    save(path, 'A_val');
    
    

