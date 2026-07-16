function template_generator(model, subsystem)
    arguments
        model string = "";
        subsystem string = "";
    end

    if model == ""
        model = "dp_interface";
        new_system(model);
    end

    open_system(model);

    if subsystem == ""
        subsystem = "IO_SUB";
        add_block("built-in/SubSystem", ...
            model + "/" + subsystem)
    end
    
    %% Initialization
    dest_subsys = find_system(model, 'Name', subsystem);
    dest_subsys = string(dest_subsys{1});
    dp_default_name = "signal1";
    dp_p_name = "port";
    dp_can_name = "CAN";
    dp_lin_name = "LIN";

    dp_sink_in = add_block("dsmpblib/Data Inport", dest_subsys + "/Sink_In");
    dp_bus_sim = add_block("dsmpblib/Data Outport", dest_subsys + "/Bus_Simulation");
    dp_sink_out = add_block("dsmpblib/Data Outport", dest_subsys + "/Sink_Out");
    dp_bus_ins = add_block("dsmpblib/Data Inport", dest_subsys + "/Bus_Inspection");
    dp_blk_arr = [dp_sink_in, dp_bus_sim, dp_sink_out, dp_bus_ins];

    glb_goto_name = "Sink_Goto";
    glb_goto_tag = "cfd_auto";

    %% Add all data port blocks and global Goto, config the port names
    for idx = 1:length(dp_blk_arr)
        dsmpb_set(dp_blk_arr(idx), dp_default_name, 'Name', dp_p_name)
        dsmpb_addsignal(dp_blk_arr(idx), dp_p_name + "." + dp_can_name)
        dsmpb_addsignal(dp_blk_arr(idx), dp_p_name + "." + dp_lin_name)
    end

    glb_goto = add_block('simulink/Signal Routing/Goto', dest_subsys{1} + "/" + glb_goto_name);
    set_param(getfullname(glb_goto), 'GotoTag', glb_goto_tag, 'TagVisibility', 'global')

    %% line setup External_In to Bus_Simulation
    add_line(dest_subsys, "Sink_In/1", "Bus_Simulation/1")
    add_line(dest_subsys, "Sink_In/1", glb_goto_name + "/1")

    %% line setup Bus_Inspection to External_Out
    add_line(dest_subsys, "Bus_Inspection/1", "Sink_Out/1")


    %% Auto arrange
    Simulink.BlockDiagram.arrangeSystem(dest_subsys);
    
end