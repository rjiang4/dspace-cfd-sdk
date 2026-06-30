%% ymal file loading and extract mapping list
% require Matlab add-on "yaml"
function DataPortUpdater(yaml_file_path, model_proj_path)

clearvars -except yaml_file_path model_proj_path
clc

if ~isempty(matlab.project.rootProject)
    close(currentProject)
end

%% load yaml file
disp("Yaml file path is: " + yaml_file_path)
yaml_file = yaml.loadFile(yaml_file_path);

%% Variant system setup
app_name = yaml_file.APPLICATIONNAME;
if app_name == "Domain"
    assignin("base", "isDomain", 1)
    assignin("base", "isSensor", 0)
elseif app_name == "SysInt" || app_name == "FunctionInt"
    assignin("base", "isDomain", 0);
    assignin("base", "isSensor", 1);
else
    assignin("base", "isDomain", 0);
    assignin("base", "isSensor", 0);
end

%% model startup
mapping_list = yaml_file.MAPPING_LIST;
asm_model_name = yaml_file.ASM_MODEL_NAME;
io_model_name = yaml_file.IO_MODEL_NAME;

addpath(genpath(model_proj_path));
openProject(model_proj_path);

can_subsystem = find_system(io_model_name, 'name', yaml_file.CAN_SUBSYSTEM_NAME);
can_subsystem = can_subsystem{1};

lin_subsystem = find_system(io_model_name, 'name', yaml_file.LIN_SUBSYSTEM_NAME);
lin_subsystem = lin_subsystem{1};

asm_bus_in = find_system(io_model_name, 'name', "ASM_BUS_In");
asm_bus_in = asm_bus_in{1};

simulated_can = find_system(io_model_name, 'name', "Sim_CAN");
simulated_can = simulated_can{1};

simulated_lin = find_system(io_model_name, 'name', "Sim_LIN");
simulated_lin = simulated_lin{1};

bus_asm_out = find_system(io_model_name, 'name', "BUS_ASM_Out");
bus_asm_out = bus_asm_out{1};

inspection_can = find_system(io_model_name, 'name', "Ins_CAN");
inspection_can = inspection_can{1};

inspection_lin = find_system(io_model_name, 'name', "Ins_LIN");
inspection_lin = inspection_lin{1};

asm_bus_out = find_system(asm_model_name, 'name', "ASM_BUS_Out");
asm_bus_out = asm_bus_out{1};

bus_asm_in = find_system(asm_model_name, 'name', "BUS_ASM_In");
bus_asm_in = bus_asm_in{1};


%% Model port block update
    function flag = data_block_updater(data_block, model_signals, varargin)
        %{
            The input num depends on the pupose of use:
            1. Update ASM blocks: ASM_BUS_Out and ASM_BUS_In
               Input: data_block, model_signals
               nargin == 2
            2. Update IO blocks: BUS_ASM_In, BUS_ASM_Out, Sim_CAN, Ins_CAN,
            Sim_LIN, Ins_LIN
               Input: data_block, model_signals, bus_type, ecu_name
               nargin == 4
               varargin{1} = bus_type
               varargin{2} = ecu_name
        %}

        flag = 0;
        data_block = convertStringsToChars(data_block);

        if nargin == 4
            % update IO model blocks
            bus_type_io = convertStringsToChars(varargin{1});
            ecu_name_io = convertStringsToChars(varargin{2});
            current_ecus = convertCharsToStrings(dsmpb_get(data_block, bus_type_io, "Elements"));
            if isempty(current_ecus) || ~ismember(ecu_name_io, current_ecus)
                flag = 1;
                % create ecu layer and add signal in the data port block
                disp("=============================")
                disp("Create " + ecu_name_io + " in " + data_block)
                for m = 1 : length(model_signals)
                    model_signal_char = convertStringsToChars(model_signals(m));
                    signal_path = {bus_type_io, ecu_name_io, model_signal_char};
                    disp("=============================")
                    disp("Adding signal " + model_signals(m) + " to " + data_block)
                    dsmpb_addsignal(data_block, signal_path)
                end
            else
                current_signals = convertCharsToStrings(dsmpb_get(data_block, {bus_type_io, ecu_name_io}, "Elements"));
                if isempty(current_signals)
                    flag = 1;
                    for m = 1 : length(model_signals)
                        model_signal_char = convertStringsToChars(model_signals(m));
                        signal_path = {bus_type_io, ecu_name_io, model_signal_char};
                        disp("=============================")
                        disp("Adding signal " + model_signals(m) + " to " + data_block)
                        dsmpb_addsignal(data_block, signal_path)
                    end
                else
                    % remove the redundant signals in current signal block
                    %if any(~ismember(current_signals, model_signals))
                    %    flag = 1;
                    %    diff_idx = find(~ismember(current_signals, model_signals));
                    %    for m = 1 : length(diff_idx)
                    %        current_signal_char = convertStringsToChars(current_signals(diff_idx(m)));
                    %        signal_path = {bus_type_io, ecu_name_io, current_signal_char};
                    %        disp("=============================")
                    %        disp("Removing signal " + current_signals(m) + " from " + data_block)
                    %        dsmpb_rmsignal(data_block, signal_path)
                    %    end
                    %end

                    % add new model signals to current signal block
                    if any(~ismember(model_signals, current_signals))
                        flag = 1;
                        diff_idx = find(~ismember(model_signals, current_signals));
                        for m = 1 : length(diff_idx)
                            model_signal_char = convertStringsToChars(model_signals(diff_idx(m)));
                            signal_path = {bus_type_io, ecu_name_io, model_signal_char};
                            disp("=============================")
                            disp("Adding signal " + model_signals(m) + " to " + data_block)
                            dsmpb_addsignal(data_block, signal_path)
                        end
                    end
                end
            end
        elseif nargin == 2
            % update ASM model blocks
            signal_port_path = 'BUS';
            current_signals = convertCharsToStrings(dsmpb_get(data_block, signal_port_path, "Elements"));
            if isempty(current_signals)
                flag = 1;
                for m = 1 : length(model_signals)
                    model_signal_char = convertStringsToChars(model_signals(m));
                    signal_path = {signal_port_path, model_signal_char};
                    disp("=============================")
                    disp("Adding signal " + model_signals(m) + " to " + data_block)
                    dsmpb_addsignal(data_block, signal_path)
                end
            else
%                 % remove the redundant signals in current signal block
%                 if any(~ismember(current_signals, model_signals))
%                     flag = 1;
%                     diff_idx = find(~ismember(current_signals, model_signals));
%                     disp(diff_idx')
%                     for m = 1: length(diff_idx)
%                         current_signal_char = convertStringsToChars(current_signals(diff_idx(m)));
%                         signal_path = {signal_port_path, current_signal_char};
%                         disp("=============================")
%                         disp("Removing signal " + current_signals(m) + " from " + data_block)
%                         dsmpb_rmsignal(data_block, signal_path)
%                     end
%                 end

                % add new model signals to current signal block
                if any(~ismember(model_signals, current_signals))
                    flag = 1;
                    diff_idx = find(~ismember(model_signals, current_signals));
                    for m = 1 : length(diff_idx)
                        model_signal_char = convertStringsToChars(model_signals(diff_idx(m)));
                        signal_path = {signal_port_path, model_signal_char};
                        disp("=============================")
                        disp("Adding signal " + model_signals(m) + " to " + data_block)
                        dsmpb_addsignal(data_block, signal_path)
                    end
                end
            end
        end
    end

if ~isequal(mapping_list, yaml.Null)
    total_sim_mapping_list = [];
    total_ins_mapping_list = [];

    %% Update IO Model
    for i = 1:length(mapping_list)
        % parse mapping list from yaml
        component_cell = struct2cell(mapping_list{i});
        % The following need to be chars as input to dsmpb_get function
        ecu_name = component_cell{2};
        signal_dir = component_cell{3};
        bus_type = component_cell{4};
        model_signals_cell = component_cell(5:end);

        % convert signals cell to array
        model_signals = [];
        for j = 1 : numel(model_signals_cell)
            model_signals = [model_signals; model_signals_cell{j}];
        end

        % remove repeat signal in the list
        model_signals = unique(model_signals, "stable");
        
        % update data port block
        if  signal_dir == "Sim"
            total_sim_mapping_list = [total_sim_mapping_list; model_signals];
            % update ASM_BUS_In data port blocks
            flag_IO = data_block_updater(asm_bus_in, model_signals, bus_type, ecu_name);
            if bus_type == "CAN"
                % update Simulated_CAN data port block
                flag_IO = data_block_updater(simulated_can, model_signals, bus_type, ecu_name);
            elseif bus_type == "LIN"
                % update Simulated_LIN data port block
                flag_IO = data_block_updater(simulated_lin, model_signals, bus_type, ecu_name);
            end
        elseif signal_dir == "Ins"
            total_ins_mapping_list = [total_ins_mapping_list; model_signals];
            % update BUS_IN_IF data port blocks
            flag_IO = data_block_updater(bus_asm_out, model_signals, bus_type, ecu_name);
            if bus_type == "CAN"
                % update Simulated_CAN data port block
                flag_IO = data_block_updater(inspection_can, model_signals, bus_type, ecu_name);
            elseif bus_type == "LIN"
                % update Simulated_LIN data port block
                flag_IO = data_block_updater(inspection_lin, model_signals, bus_type, ecu_name);
            end
        else
            disp("Signal direction not defined...")
            exit()
        end
    end

    %% update ASM To_BUS block
    total_sim_mapping_list = unique(total_sim_mapping_list, "stable");
    total_ins_mapping_list = unique(total_ins_mapping_list, "stable");
    flag_ASM_sim = data_block_updater(asm_bus_out, total_sim_mapping_list);
    flag_ASM_ins = data_block_updater(bus_asm_in, total_ins_mapping_list);

    if flag_ASM_sim == 1 || flag_ASM_ins == 1
        flag_ASM = 1;
    else
        flag_ASM = 0;
    end
%     current_asm_signals = dsmpb_get(asm_bus_out, "To_BUS", "Elements");
%     first_signal_in_total_sim = convertStringsToChars(total_sim_mapping_list(1));
%     if ~isempty(current_asm_signals)
%         if length(current_asm_signals) > 1
%             for i = 2 : length(current_asm_signals)
%                 current_asm_signal = current_asm_signals{i};
%                 dsmpb_rmsignal(asm_bus_out, {'To_BUS', current_asm_signal})
%             end
%             dsmpb_set(asm_bus_out, {'To_BUS', current_asm_signals{1}}, "Name", first_signal_in_total_sim)
%         end
%     else
%         dsmpb_addsignal(asm_bus_out, {'To_BUS', first_signal_in_total_sim})
%     end
%     for i = 2 : length(total_sim_mapping_list)
%         model_signal = convertStringsToChars(total_sim_mapping_list(i));
%         add_signal(asm_bus_out, {'To_BUS', model_signal})
%     end
% 
%     % update ASM From_BUS block
%     current_asm_signals = dsmpb_get(bus_asm_in, "From_BUS", "Elements");
%     first_signal_in_total_ins = convertStringsToChars(total_ins_mapping_list(1));
%     if ~isempty(current_asm_signals)
%         if length(current_asm_signals) > 1
%             for i = 2 : length(current_asm_signals)
%                 current_asm_signal = current_asm_signals{i};
%                 dsmpb_rmsignal(bus_asm_in, {'From_BUS', current_asm_signal})
%             end
%             dsmpb_set(bus_asm_in, {'From_BUS', current_asm_signals{1}}, "Name", first_signal_in_total_ins)
%         end
%     else
%         dsmpb_addsignal(bus_asm_in, {'From_BUS', first_signal_in_total_ins})
%     end
%     for i = 2 : length(total_ins_mapping_list)
%         model_signal = convertStringsToChars(total_ins_mapping_list(i));
%         add_signal(bus_asm_in, {'From_BUS', model_signal})
%     end
else
    disp('No mapping signal available...')
end

opened_models = get_param(Simulink.allBlockDiagrams('model'),'Name');
for i = 1 : length(opened_models)
    save_system(opened_models{i})
    disp("System saved: " + opened_models{i})
end

if flag_IO == 0
    disp("------------------------------------------------")
    disp("No update for IO Model Port Block")
    disp("------------------------------------------------")
else
    disp("------------------------------------------------")
    disp("IO Model Port Block Updated!")
    disp("------------------------------------------------")
end

if flag_ASM == 0
    disp("------------------------------------------------")
    disp("No update for ASM Model Port Block")
    disp("------------------------------------------------")
else
    disp("------------------------------------------------")
    disp("ASM Model Port Block Updated!")
    disp("------------------------------------------------")
end

end