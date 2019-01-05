#pragma once

#include "IPlug_include_in_plug_hdr.h"
#include "IPlugBase.h"

#include "MikaMicro.h"

// for text I/O
#include <fstream>
#include <string>
using namespace std;

class PresetMenu : public IPanelControl
{
private:
	WDL_String mPreviousPath;

public:
	PresetMenu(IPlugBase *pPlug, IRECT pR)
		: IPanelControl(pPlug, pR, &COLOR_BLUE)
	{}

	bool Draw(IGraphics* pGraphics)
	{
		pGraphics->FillIRect(&COLOR_WHITE, &mRECT);

		int ax = mRECT.R - 8;
		int ay = mRECT.T + 4;
		int bx = ax + 4;
		int by = ay;
		int cx = ax + 2;
		int cy = ay + 2;

		pGraphics->FillTriangle(&COLOR_GRAY, ax, ay, bx, by, cx, cy, &mBlend);

		return true;
	}

	void OnMouseDown(int x, int y, IMouseMod* pMod)
	{
		if (pMod->L)
		{
			doPopupMenu();
		}

		Redraw(); // seems to need this
		SetDirty();
	}

	void doPopupMenu()
	{
		IPopupMenu menu;

		IGraphics* gui = mPlug->GetGUI();

		menu.AddItem("Previous preset");
		menu.AddItem("Next preset");
		menu.AddSeparator();
		menu.AddItem("Save Program...");
		menu.AddItem("Save Bank...");
		menu.AddSeparator();
		menu.AddItem("Load Program...");
		menu.AddItem("Load Bank...");
		menu.AddSeparator();
		menu.AddItem("Dump preset...");
		menu.AddSeparator();
		menu.AddItem("Save values as text only...");
		menu.AddItem("Load from values as text...");
		menu.AddSeparator();
		menu.AddItem("Export general param info as csv...");
		menu.AddSeparator();
		menu.AddItem("Set osc 2 coarse to that of osc 1");


		if (gui->CreateIPopupMenu(&menu, &mRECT))
		{
			const char* paramEnumNames[] =
			{
				"kOsc1Wave",
				"kOsc1Coarse",
				"kOsc1Fine",
				"kOsc1Split",
				"kOsc2Wave",
				"kOsc2Coarse",
				"kOsc2Fine",
				"kOsc2Split",
				"kOscMix",
				"kFmMode",
				"kFmCoarse",
				"kFmFine",
				"kFilterEnabled",
				"kFilterCutoff",
				"kFilterResonance",
				"kFilterKeyTrack",
				"kVolEnvA",
				"kVolEnvD",
				"kVolEnvS",
				"kVolEnvR",
				"kVolEnvV",
				"kModEnvA",
				"kModEnvD",
				"kModEnvS",
				"kModEnvR",
				"kModEnvV",
				"kLfoAmount",
				"kLfoFrequency",
				"kLfoDelay",
				"kVolEnvFm",
				"kVolEnvCutoff",
				"kModEnvFm",
				"kModEnvCutoff",
				"kLfoFm",
				"kLfoCutoff",
				"kVoiceMode",
				"kGlideSpeed",
				"kMasterVolume",
			};

			int itemChosen = menu.GetChosenItemIdx();
			WDL_String fileName;

			//printf("chosen %i /n", itemChosen);
			switch (itemChosen)
			{
			case 0:
				mPlug->RestorePreset(mPlug->GetCurrentPresetIdx() - 1);
				break;
			case 1:
				mPlug->RestorePreset(mPlug->GetCurrentPresetIdx() + 1);
				break;
			case 3: //Save Program
				fileName.Set(mPlug->GetPresetName(mPlug->GetCurrentPresetIdx()));
				GetGUI()->PromptForFile(&fileName, kFileSave, &mPreviousPath, "fxp");
				mPlug->SaveProgramAsFXP(&fileName);
				break;
			case 4: //Save Bank
				fileName.Set("IPlugChunksBank");
				GetGUI()->PromptForFile(&fileName, kFileSave, &mPreviousPath, "fxb");
				mPlug->SaveBankAsFXB(&fileName);
				break;
			case 6: //Load Preset
				GetGUI()->PromptForFile(&fileName, kFileOpen, &mPreviousPath, "fxp");
				mPlug->LoadProgramFromFXP(&fileName);
				break;
			case 7: //Load Bank
				GetGUI()->PromptForFile(&fileName, kFileOpen, &mPreviousPath, "fxb");
				mPlug->LoadBankFromFXB(&fileName);
				break;
			case 9: //Dump Preset
				fileName.Set("preset");
				GetGUI()->PromptForFile(&fileName, kFileSave, &mPreviousPath, "txt");
				mPlug->DumpPresetSrcCode(fileName.Get(), paramEnumNames);
				break;
			case 11: //Save param values to text
				fileName.Set("preset_text");
				GetGUI()->PromptForFile(&fileName, kFileSave, &mPreviousPath, "txt");
				DumpPresetText(fileName.Get(), paramEnumNames);
				break;
			case 12: //Load param values from text
				GetGUI()->PromptForFile(&fileName, kFileOpen, &mPreviousPath, "txt");
				LoadPresetText(fileName.Get(), paramEnumNames);		
				break;
			case 14: //Export param info
				fileName.Set("param_info");
				GetGUI()->PromptForFile(&fileName, kFileSave, &mPreviousPath, "csv");
				ExportParamInfo(fileName.Get(), paramEnumNames);
			case 16: //Set osc2 coarse to that of osc1
				GetGUI()->SetParameterFromGUI(5, mPlug->GetParam(1)->GetNormalized());
			default:
				break;
			}
		}
	}

	// MY OWN
	void PresetMenu::DumpPresetText(const char* filename, const char* paramEnumNames[])
	{
		int i, n = mPlug->NParams();
		FILE* fp = fopen(filename, "w");
		//fprintf(fp, "  MakePresetFromNamedParams(\"name\", %d", n);
		for (i = 0; i < n; ++i)
		{
			IParam* pParam = mPlug->GetParam(i);
			char paramVal[32];
			switch (pParam->Type())
			{
			case IParam::kTypeBool:
				sprintf(paramVal, "%s", (pParam->Bool() ? "true" : "false"));
				break;
			case IParam::kTypeInt:
				sprintf(paramVal, "%d", pParam->Int());
				break;
			case IParam::kTypeEnum:
				sprintf(paramVal, "%d", pParam->Int());
				break;
			case IParam::kTypeDouble:
			default:
				sprintf(paramVal, "%.6f", pParam->Value());
				break;
			}
			//fprintf(fp, "%s\n%s\n", paramEnumNames[i], paramVal);
			fprintf(fp, "%s\n", paramVal);
		}
		//fprintf(fp, ");\n");
		fclose(fp);
	}

	// MY OWN
	void PresetMenu::LoadPresetText(const char * filename, const char * paramEnumNames[])
	{

		std::ifstream infile(filename);

		int i = 0;
		for (string line; getline(infile, line); )
		{
			IParam* pParam = mPlug->GetParam(i);
			double nonNormalizedValue = 0;
			switch (pParam->Type())
			{
			case IParam::kTypeBool:
				nonNormalizedValue = (line == "true") ? 1 : 0;
				break;
			case IParam::kTypeInt:
				nonNormalizedValue = stoi(line);
				break;
			case IParam::kTypeEnum:
				nonNormalizedValue = stoi(line);
				break;
			case IParam::kTypeDouble:
			default:
				nonNormalizedValue = stod(line);
				break;
			}
			GetGUI()->SetParameterFromGUI(i, pParam->GetNormalized(nonNormalizedValue));
			i++;
		}

		infile.close();

	}

	// MY OWN
	void PresetMenu::ExportParamInfo(const char * filename, const char * paramEnumNames[])
	{
		int i, n = mPlug->NParams();
		FILE* fp = fopen(filename, "w");
		fprintf(fp, "name,type,min,max\n");
		for (i = 0; i < n; ++i)
		{
			IParam* pParam = mPlug->GetParam(i);
			double min, max;
			pParam->GetBounds(&min, &max);
			string smin, smax;
			string paramType;
			switch (pParam->Type())
			{
			case IParam::kTypeBool:
				paramType = "boolean";
				smin = to_string((int)round(min));
				smax = to_string((int)round(max));
				break;
			case IParam::kTypeInt:
				paramType = "int";
				smin = to_string((int)round(min));
				smax = to_string((int)round(max));
				break;
			case IParam::kTypeEnum:
				paramType = "enum";
				smin = to_string((int)round(min));
				smax = to_string((int)round(max));
				break;
			case IParam::kTypeDouble:
			default:
				paramType = "double";
				smin = to_string(min);
				smax = to_string(max);
				break;
			}
			fprintf(fp, "%s,%s,%s,%s\n", paramEnumNames[i], paramType.c_str(), smin.c_str(), smax.c_str());
		}
		fclose(fp);
	}

};