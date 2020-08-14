#ifndef OCTREE_H1
#define OCTREE_H1
#include "stdafx.h"
#include <math.h>
#include <vector>
#include <string>
#include <fstream>

using namespace std;

#define MAX_ELE_NUM 1		//�ڵ���������λ�õ����

struct Node{
	int eul[3];
	Node *next;
};

/*�ռ����MBR���귶Χ*/
class MapRect{
public:
	int minE1, maxE1, minE2, maxE2, minE3, maxE3;

public:
	MapRect(int minE1, int maxE1, int minE2, int maxE2, int minE3, int maxE3);
};

/*�ռ����MBR��Ϣ*/
class ElePoint
{
public:
	int eul[6];
	Node p;
	//bool prior;

public:
	ElePoint();
	ElePoint(int Eelbow1, int Eelbow2, int Eelbow3, int Ewrist1, int Ewrist2, int Ewrist3);
};

class OCTreeNode {
public:
	string ID;            //��0���ң�1���ϣ�0���£�1��ǰ��0����1
	bool isLeaf;        //�Ƿ���Ҷ�ӽڵ�
	MapRect* Box;        //�ڵ����ľ�������
	int nEleCount;        //�ڵ����������λ�ø������
	int aCount;				//�ڵ����������λ����Ŀ����
	int testCount;
	ElePoint elePointObj[MAX_ELE_NUM];        //λ�õ��б�,���2000��
	OCTreeNode* LUF;        //����ǰ
	OCTreeNode* LDF;        //����ǰ
	OCTreeNode* RUF;        //����ǰ
	OCTreeNode* RDF;        //����ǰ
	OCTreeNode* LUL;        //���Ϻ�
	OCTreeNode* LDL;        //���º�
	OCTreeNode* RUL;        //���Ϻ�
	OCTreeNode* RDL;        //���º�

public:
	//һ��node�Ĺ��캯����������һ�������壨�����壩�ĳ���ߣ����д���λ�õ�string
	OCTreeNode(MapRect box, string id);
	//��һ��octreenode ����һ����Ŀ
	void InsertEle(ElePoint elePoint);
	//��һ��octreenode 
	void SplitNode();
	//�ж�һ����Ŀ�Ƿ�����һ��octreenode
	bool isContain(ElePoint elePoint);
	OCTreeNode* SelectElePoint(ElePoint elePoint);
	string* selectNeiborID();
	void getElePointFromIDs(string* seleIDs, vector<OCTreeNode*>& neiborNodes);
	OCTreeNode* getElePointFromID(string seleID);
	string getID();
	void handleOCTreeNode(OCTreeNode myNode, double diry, double dirz, double dis);
	int getEleCount();
	ElePoint* getElePoint();

	//void TraverseTree();
};

class OCTree{
public:
	OCTreeNode* root;

public:
	static void SplitString(string str, vector<string>& v, string sep);
	void createOCTree();
};
#endif


  
