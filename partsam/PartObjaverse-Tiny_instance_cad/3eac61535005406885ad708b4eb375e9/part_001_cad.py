"""Standalone mesh-derived CAD code, with embedded vertex and triangle data.

This reconstructs a faceted BREP, not an inferred sketch/extrusion feature tree.
Original numeric coordinates are retained; physical STL units are unknown.
Open meshes remain CAD surfaces. No guessed closures or thickness are added.
Run: python part_XXX_cad.py [--output-directory PATH] [--no-validate]
"""
from pathlib import Path
import argparse,base64,io,json,time,zlib
import numpy as np
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3eac61535005406885ad708b4eb375e9/part_001.stl', 'relative_path': '3eac61535005406885ad708b4eb375e9/part_001.stl', 'source_sha256': '2b6bcfbdc23acda242b518f796d0d1c744020c5a37a01060e628d9e9f77395e0', 'input_faces': 178, 'input_vertices': 129, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08643770217895508, 0.06576815247535706, -0.13908728957176208], [0.14277362823486328, 0.12618526816368103, 0.17555926740169525]]}
GEOMETRY_BASE85 = 'c$}qJ2~bt%6~4kl0f`F`YoduyQv}h1EFyxD7d48q2r3a=;312EvdBXa4Dwv6W=w=u7}2;qjoGL>8bvKWjarN`5GFFX)I4XblE$>gkxXjP^xpG*nrEk->9ow8`M&#|^Phh^|9|fzF3M5oso-z0;_|L}NUfWqXy&GPD#aOvMcHW?CcnIb(r!v0(Y3!PxG^>%CN8O)QmicVPR}r<6?%v1y~k#TdXLb1XXY0c6{hB;<QJxAX!@koMWzf@H)W+3WT?+R0fA#i=!1rh(3k7~$3ItX3{Cn^PN`tNdii98iiXaTPc>A|_lE8q-KafV+v1>i+^iSf@!D~TS1PTd7rzC)(*t?_+;vLy9~usce)jq?dH!k7AEAE){rYXhzY~5|^tY>_yUs(ud7jYM6+*udBk?wCfb_2{_k;d*Lxbe0>Np|#MB72py>HfQ&-#dX@hgUA=pCm%(Vi{k(-6PC9QsJF!_sd|6XG9^g`SpsRG#aKp^xx_zP&@nVLm_XwCIW79uPgbOZv5ZUxs<>TcB4B#(Y<7!n*D53q9qph?~*gh;?w<FS_Sh%&Wr#>o%}?pXjSD$@rBWDUwgAs@p62&t)=B<Ha>tpShLLF9yoI45o+BJ@4)j{U0u(TWr6>yq2DXUezh%w_V0QE1?z8H)lwH=4w~;`_;ud(GQo@qYf@%ovNln_ehiVwQbmp`B|HmN&Cz?)W`QPAb-o&6{6S0Vn0^4Vmua?m7@E%9guxo(1|=Fo1jOfq2F+S#20j|7Jc)3$Zv?idKxp<h(0^~kmNa(gnq15Ya{IH%FvjMb#CduF2b&Utd7$$-vg`P5q;}9$*<pBBz2%12&fX>9rM*E>Yy9{1iku-jNj1KCHty0J%V13bu%swkUCHg;P0hBOHZi}eP;eS>DPHywZuP&l=0gtCLcn-ccClUI2R2|&*Qv2UnBacGcr!w&CDYbKk^UIYq5{|4f76ToadoeV&C=6e)Z4jKcY_brkj{oOX()jKSN#FMo&Pza}D&zti!5ijC0+LTG4B;4*E*ggFY2H>+os4t=j~hb!GOufcSNuTO#c0*|z0X?2At(^p!XlmZmM3m(>Kl6YKW0{zL1aKRHL~r?Kw^F7Jx&fpe#KpN4gNs$+l6ra7p$_6X=aFG}*?QCA%kw~4+Db)xK9i}=J-(35fAEjOKxO8zXz?WkMqi)H^E%&TBBbU)O;;ZeMtL#3k}`c%}vb@w^wiDP$&J`eYg?ba65)%75Y=pW;JS<lqVy`W6Yfj%Gio3Xj_;4^v%>*pcw?T!=BD{+t6I%6BK&bOc^;e6TL3(;@ledzwUSB-8rkiTofPSG=P4;YemU_4uEpl`#yYKzJ~F1lMC^r5`ZM;ei*y%qW$+~>9)b5MuY_jieY1MdZW%y-b!FN<#7InataZL^AAdk^tVe82PyLfsx#c8mTg-e1O5AEF+NMbK+;&loo}BED+{bjS6Q$GY{>Y0+=Zd|z}Iyw?oTz0hy;dg#~i9<=6+g8t)U=nwEdHKyH0o$P7<Ky(M36Jvvd^*=W5L&>`f^RhkYhkHY(`$*z-7>^}VkNY96#~#sp;Qg*Q#y3iyyCKl8;Cn#7Z3pzYroGsgmkvt5%6^GcYNzZI{dgVDY3^U3dphrz@$eqA`DZiF0@2OUl~RYs3xU#JxmN^z=N+u)tWtSa){K|BH~*Z4`}t@P*2lLRdhRG0kJ<aYte5im5_GQ?ynm~^ptpx1u4XCje<c?EPBcQ#G~m5|b%4xMS-B7T>JvEc!#j|t$_w{MkKUM9bQ1Kl{-T?IdJ%cb-7x;o=0o3JC+Ew$p%eMHu7@6yh;wmmoa~c&FG1I(h^{;tXVD$#o3{uWy)$ILmB_(Z_ZBnuw=qHHul#Kl^t?0ZcVpPcqR&1K{mW)qXY)9(gP7Oldi!;-?S2L0X}SkJtPJB!dIbH8V0ktt{DAv&r61-S`6cv<Z{*xrI$SZHWBrey{`aDuzcwPzg9PYaz3|<z)>J20=qY*4M|AkU+IR)}RUgp}gB<bwROpL5w>KcZ#!33MR$I_-pH|6h{#=jmsBd+s&!!v4kT($Hsi?s^tnQLHbL)NS*K+SW=qG(Jjwj!rCqKtNmQ6x^xby<<D93(vEy4QkjKujWn2Y@k-X*%VRfqcNen;l7d}T$vsTJQ>J#!Er_%`mT4|4Dw6M7%>+I|pv$ph^BqAuubzJR`ICeCkkDfXvdtbCtZ+lGqY`rA0{SJtF65<jK}_s^{92O{F0`Bjtr-YjFgvwDJ5b5VcQWTx8vq|rp}?+O0<pETLQ|J_fT(V_qEPnsTzHb`~4s`Xdx1#%64MXpWldDYyB9^^ggb0xZy_oB~@=t}O+wta|w$zAEw5&Mw4(dSImk$ceBm*{MlOT*`gy~%a-IS`*Ccc#yg=s@0=zTQMfyIdMN5xbK+(5Dcc$Q|kHMpVdq)7PEYjXXuQMAc@IYq)?ok9+}nvTA9JPa)TEA#nluLUJvBxoTyqWf618&Gh9Hv&bvxD<tNVm(iC)EF{-#4%=%uo4kT;%*5s7sjAIq-ucXv&o;9;r`eoinw@VUF^xQ#xfT-h$rq`Xp;`ekn>>@gTw(#ak-l_dE_ngl77-Vd=h9~)7LljZmq#>_XVbTsm}i$u!==O$aua>U#HHkU^erJ4lP{*Pgt){mmxkrUH_40XTShD=UqW9gaT$3DeQy#=$tS4xs%m4&HS{L_n%tY*OSQ?2pFpnRaH2Q)aB?kvu4+lDMG<4jW9joHMv+gYZy3>+Jc+&-;xKZ}UT1p^Bgm(+O)POP`75doVcsFk<I6S?oKpnnIN8oOoH&`>i@AmqeaU~L+6dKxh<@Y~>5C)=k&mO#K#U|0V%soc2zexZ(Zn!v1ASA7(d2&gg%GFM<<f8xaXfi6ebb4P$fwX3Pn=F3Lf?2|yj?C0<A~G9r_=WaF^)W*z69bM<m2g^Mob_dq}ofW4J6kvnCMR)Odg<UuXe-_BG)jK7)%~YuEqPPHdN8Roq;ct&!jJ$s3)I6-)qEh@}cy-Oni-8vlrQ3!vW+o*k&fthkUeZW0-dg^Mtd_0M2Ou=Q!BT7fKvV9>83o#BlOJ)kdl|O52mDZVsM~|LI@7zx<iCm)|r0`2E+G&wftXw`@}rJ^i?fi*nN5q3Vm)K`z2?v@aFqpPylT-2'

def decode_geometry():
    with np.load(io.BytesIO(zlib.decompress(base64.b85decode(GEOMETRY_BASE85)))) as data:
        return data['vertices'],data['faces']

def build():
    vertices,faces=decode_geometry()
    center=(vertices.min(axis=0)+vertices.max(axis=0))/2
    extent=float(np.ptp(vertices,axis=0).max())
    if extent<=0: raise ValueError('Source has zero extent')
    construction_scale=100.0/extent
    v=(vertices-center)*construction_scale
    sewing=BRepBuilderAPI_Sewing(1e-7,True,True,True,False)
    planar_faces=[]
    skipped=[]
    for index,tri in enumerate(faces):
        points=v[tri]
        if np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))<=1e-12:
            skipped.append(index)
            continue
        wire=cq.Wire.makePolygon([cq.Vector(*p) for p in points],close=True)
        face=cq.Face.makeFromWires(wire)
        planar_faces.append(face)
        sewing.Add(face.wrapped)
    if not planar_faces: raise ValueError('No non-degenerate triangles')
    sewing.Perform()
    shape=cq.Shape.cast(sewing.SewedShape())
    representation='faceted_surface'
    if SOURCE_INFO['input_watertight']:
        solids=[]
        for shell in shape.Shells():
            solid=cq.Solid.makeSolid(shell)
            if solid.Volume()<0: solid=cq.Shape.cast(solid.wrapped.Reversed())
            solids.append(solid)
        if solids:
            candidate=solids[0] if len(solids)==1 else cq.Compound.makeCompound(solids)
            if candidate.isValid() and len(candidate.Faces())==len(planar_faces):
                shape=candidate
                representation='faceted_solid'
    if not shape.isValid():
        # Explicitly represent troublesome nonmanifold edges as separate faces.
        shape=cq.Compound.makeCompound(planar_faces)
        representation='independent_faces'
    shape=shape.scale(1/construction_scale).translate(tuple(center))
    return shape,{'representation':representation,'degenerate_faces_skipped':skipped,
                  'construction_scale':construction_scale,
                  'sewing_tolerance_original_units':1e-7/construction_scale}

def describe(shape):
    b=shape.BoundingBox()
    return {'valid':bool(shape.isValid()),'solids':len(shape.Solids()),
            'shells':len(shape.Shells()),'faces':len(shape.Faces()),
            'bounds':[[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]],
            'solid_volume':float(shape.Volume()) if shape.Solids() else None}

def export(out,validate=True):
    start=time.time();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    shape,metadata=build()
    state=describe(shape)
    if not state['valid']: raise RuntimeError('Constructed BREP is invalid')
    shape.exportBrep(str(out/(PART_NAME+'.brep')))
    shape.exportStep(str(out/(PART_NAME+'.step')))
    report={**SOURCE_INFO,**metadata,'cad':state,'step_unit':'mm',
            'source_physical_unit':'unknown','coordinate_policy':'preserve original numeric coordinates',
            'code_kind':'standalone embedded faceted geometry','source_modified':False}
    if validate:
        reopened=cq.importers.importStep(str(out/(PART_NAME+'.step'))).val()
        report['step_reimport']=describe(reopened)
        if not report['step_reimport']['valid']: raise RuntimeError('Reimported STEP is invalid')
        if report['step_reimport']['faces']!=state['faces']:
            raise RuntimeError('STEP transfer changed the face count')
        error=float(np.max(np.abs(np.asarray(report['step_reimport']['bounds'])-np.asarray(state['bounds']))))
        report['roundtrip_bounds_max_error']=error
        if error>max(float(np.ptp(decode_geometry()[0],axis=0).max())*1e-5,1e-6):
            raise RuntimeError('STEP transfer changed bounding dimensions')
    report['seconds']=time.time()-start
    report['status']='SUCCESS'
    (out/(PART_NAME+'_report.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--no-validate',action='store_true')
    args=parser.parse_args()
    print(json.dumps(export(args.output_directory,not args.no_validate)),flush=True)
